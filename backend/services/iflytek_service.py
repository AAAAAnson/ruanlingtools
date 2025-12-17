# -*- coding: utf-8 -*-
"""
iFlytek (讯飞) Speech Recognition Service
使用讯飞语音转写API实现高准确度的中文语音识别
"""

import base64
import hashlib
import hmac
import json
import time
import os
from datetime import datetime
from urllib.parse import urlencode
from pathlib import Path
import websocket
import _thread as thread
from typing import Optional, Dict, Any
import logging
import ffmpeg

from config import IFLYTEK_APPID, IFLYTEK_API_SECRET, IFLYTEK_API_KEY

logger = logging.getLogger(__name__)


class IFlytekASR:
    """
    讯飞语音识别服务类
    使用WebSocket实时流式识别API
    """

    def __init__(self):
        self.appid = IFLYTEK_APPID
        self.api_secret = IFLYTEK_API_SECRET
        self.api_key = IFLYTEK_API_KEY
        self.result_text = ""
        self.error_message = ""

    def convert_audio_to_pcm(self, input_path: str, output_path: str) -> bool:
        """
        将音频文件转换为PCM格式 (16kHz, 16bit, mono)

        Args:
            input_path: 输入音频文件路径
            output_path: 输出PCM文件路径

        Returns:
            转换是否成功
        """
        try:
            logger.info(f"开始转换音频: {input_path} -> {output_path}")

            # 使用ffmpeg转换为PCM格式
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                format='s16le',  # PCM signed 16-bit little-endian
                acodec='pcm_s16le',
                ac=1,  # 单声道
                ar='16000'  # 采样率16kHz
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)

            logger.info(f"音频转换成功: {output_path}")
            return True

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg转换失败: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            logger.error(f"音频转换异常: {str(e)}")
            return False

    def create_url(self):
        """
        生成鉴权URL
        """
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # 拼接字符串
        signature_origin = f"host: iat-api.xfyun.cn\ndate: {date}\nGET /v2/iat HTTP/1.1"

        # 进行hmac-sha256加密
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求参数拼接到URL
        params = {
            "authorization": authorization,
            "date": date,
            "host": "iat-api.xfyun.cn"
        }

        url = f"wss://iat-api.xfyun.cn/v2/iat?{urlencode(params)}"
        return url

    def transcribe_file(
        self,
        audio_file_path: str,
        language: str = "zh_cn",
        output_format: str = "txt"
    ) -> Dict[str, Any]:
        """
        转录音频文件

        Args:
            audio_file_path: 音频文件路径
            language: 语言代码 (zh_cn, en_us等)
            output_format: 输出格式

        Returns:
            包含转录结果的字典
        """
        pcm_file_path = None
        try:
            self.result_text = ""
            self.error_message = ""

            # 将音频转换为PCM格式
            pcm_file_path = str(Path(audio_file_path).with_suffix('.pcm'))
            if not self.convert_audio_to_pcm(audio_file_path, pcm_file_path):
                return {
                    "success": False,
                    "error": "音频格式转换失败"
                }

            # 读取PCM音频数据
            with open(pcm_file_path, 'rb') as f:
                audio_data = f.read()

            # 计算音频时长（PCM 16kHz 16bit mono = 32000 bytes/s）
            duration_seconds = len(audio_data) / 32000
            logger.info(f"音频时长: {duration_seconds:.1f}秒")

            # 讯飞IAT API限制约60秒，超过则分段处理
            MAX_SEGMENT_SECONDS = 50  # 留点余量，使用50秒
            if duration_seconds > MAX_SEGMENT_SECONDS:
                logger.info(f"音频超过{MAX_SEGMENT_SECONDS}秒，启用分段处理")
                return self._transcribe_long_audio(audio_data, language, duration_seconds)

            # 短音频直接处理
            return self._transcribe_segment(audio_data, language)

        except Exception as e:
            logger.error(f"讯飞语音识别失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

        finally:
            # 清理临时PCM文件
            if pcm_file_path and os.path.exists(pcm_file_path):
                try:
                    os.remove(pcm_file_path)
                    logger.info(f"已删除临时PCM文件: {pcm_file_path}")
                except Exception as e:
                    logger.warning(f"删除临时PCM文件失败: {str(e)}")

    def _transcribe_long_audio(
        self,
        audio_data: bytes,
        language: str,
        total_duration: float
    ) -> Dict[str, Any]:
        """
        分段处理长音频

        Args:
            audio_data: PCM音频数据
            language: 语言代码
            total_duration: 总时长(秒)

        Returns:
            转录结果字典
        """
        try:
            SEGMENT_SECONDS = 50  # 每段50秒
            bytes_per_second = 32000  # PCM 16kHz 16bit mono
            segment_size = SEGMENT_SECONDS * bytes_per_second

            all_text = []
            total_segments = (len(audio_data) + segment_size - 1) // segment_size

            logger.info(f"将{total_duration:.1f}秒音频分为{total_segments}段处理")

            for i in range(0, len(audio_data), segment_size):
                segment_num = i // segment_size + 1
                segment_data = audio_data[i:i + segment_size]
                segment_duration = len(segment_data) / bytes_per_second

                logger.info(f"正在处理第{segment_num}/{total_segments}段 ({segment_duration:.1f}秒)")

                # 重置result_text
                self.result_text = ""
                self.error_message = ""

                # 转录这一段
                result = self._transcribe_segment(segment_data, language)

                if not result.get("success"):
                    logger.error(f"第{segment_num}段转录失败: {result.get('error')}")
                    return {
                        "success": False,
                        "error": f"第{segment_num}段转录失败: {result.get('error')}"
                    }

                segment_text = result.get("text", "").strip()
                if segment_text:
                    all_text.append(segment_text)
                    logger.info(f"第{segment_num}段完成，获得{len(segment_text)}字符")

                # 段间稍作延迟，避免频繁请求
                if i + segment_size < len(audio_data):
                    time.sleep(0.5)

            # 合并所有段落
            final_text = "".join(all_text)
            logger.info(f"所有{total_segments}段处理完成，总共{len(final_text)}字符")

            return {
                "success": True,
                "text": final_text,
                "language": language,
                "engine": "iflytek",
                "segments": total_segments
            }

        except Exception as e:
            logger.error(f"分段转录失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _transcribe_segment(
        self,
        audio_data: bytes,
        language: str
    ) -> Dict[str, Any]:
        """
        转录单个音频段

        Args:
            audio_data: PCM音频数据
            language: 语言代码

        Returns:
            转录结果字典
        """
        try:
            # 创建WebSocket连接
            ws_url = self.create_url()

            def on_message(ws, message):
                """接收消息回调"""
                try:
                    data = json.loads(message)
                    code = data.get('code')

                    # 记录原始消息用于调试（仅记录关键信息）
                    logger.debug(f"收到消息 - 错误码: {code}, 数据状态: {data.get('data', {}).get('status', 'N/A')}")

                    if code != 0:
                        self.error_message = data.get('message', '识别失败')
                        logger.error(f"识别失败，错误码: {code}, 错误信息: {self.error_message}")
                        logger.error(f"完整错误响应: {json.dumps(data, ensure_ascii=False)}")
                        ws.close()
                        return

                    # 提取识别结果
                    result = data.get('data', {}).get('result', {})
                    ws_list = result.get('ws', [])

                    # 只保存最终结果（ls=true），避免中间结果重复
                    # ls (last slice): 表示这个句子的最后一个分片
                    current_text = ""
                    for ws_item in ws_list:
                        # 检查是否是最后一个分片
                        is_last_slice = ws_item.get('ls', False)
                        if is_last_slice:
                            for cw in ws_item.get('cw', []):
                                w = cw.get('w', '')
                                current_text += w
                                self.result_text += w

                    if current_text:
                        logger.info(f"收到最终识别结果: {current_text[:50]}... (当前总长度: {len(self.result_text)}字符)")

                    # 如果是最后一帧,关闭连接
                    status = data.get('data', {}).get('status')
                    if status == 2:
                        logger.info(f"收到结束标记，最终文本长度: {len(self.result_text)}字符")
                        ws.close()

                except Exception as e:
                    logger.error(f"处理消息时出错: {str(e)}")
                    self.error_message = str(e)
                    ws.close()

            def on_error(ws, error):
                """错误回调"""
                logger.error(f"WebSocket错误: {error}")
                logger.error(f"错误类型: {type(error).__name__}")
                self.error_message = str(error)

            def on_close(ws, close_status_code, close_msg):
                """关闭连接回调"""
                logger.info(f"WebSocket连接已关闭 - 状态码: {close_status_code}, 消息: {close_msg}")
                if close_status_code and close_status_code != 1000:
                    logger.warning(f"非正常关闭 - 状态码: {close_status_code}")

            def on_open(ws):
                """打开连接回调"""
                def run():
                    try:
                        # 发送音频数据
                        frame_size = 8000  # 每次发送8KB
                        interval = 0.04  # 40ms间隔

                        audio_size_mb = len(audio_data) / (1024 * 1024)
                        logger.info(f"准备发送音频数据: {audio_size_mb:.2f}MB, 共{len(audio_data)}字节")

                        # 发送开始帧
                        params = {
                            "common": {
                                "app_id": self.appid
                            },
                            "business": {
                                "language": language,
                                "domain": "iat",
                                "accent": "mandarin",
                                "vad_eos": 30000,  # 增加到30秒，避免长音频被截断
                                "dwa": "wpgs"  # 开启动态修正
                            },
                            "data": {
                                "status": 0,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": ""
                            }
                        }
                        ws.send(json.dumps(params))
                        logger.info("已发送开始帧")

                        # 分块发送音频数据
                        total_chunks = (len(audio_data) + frame_size - 1) // frame_size
                        for i in range(0, len(audio_data), frame_size):
                            # 检查连接是否还活着
                            if not ws.sock or not ws.sock.connected:
                                logger.error(f"发送到第 {i} 字节时连接已断开")
                                self.error_message = "WebSocket连接在发送过程中断开"
                                break

                            chunk = audio_data[i:i + frame_size]
                            encoded = base64.b64encode(chunk).decode('utf-8')

                            status = 1  # 中间帧
                            if i + frame_size >= len(audio_data):
                                status = 2  # 最后一帧

                            params["data"]["status"] = status
                            params["data"]["audio"] = encoded

                            ws.send(json.dumps(params))

                            # 每发送100个chunk记录一次进度
                            chunk_num = i // frame_size + 1
                            if chunk_num % 100 == 0 or status == 2:
                                progress = (i / len(audio_data)) * 100
                                logger.info(f"发送进度: {progress:.1f}% ({chunk_num}/{total_chunks} chunks)")

                            time.sleep(interval)

                        logger.info("所有音频数据已发送完毕")

                    except Exception as e:
                        logger.error(f"发送音频数据时出错: {str(e)}")
                        self.error_message = str(e)
                        ws.close()

                thread.start_new_thread(run, ())

            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.on_open = on_open
            ws.run_forever()

            # 检查错误
            if self.error_message:
                return {
                    "success": False,
                    "error": self.error_message
                }

            # 返回结果
            return {
                "success": True,
                "text": self.result_text.strip(),
                "language": language,
                "engine": "iflytek"
            }

        except Exception as e:
            logger.error(f"段音频识别失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


def transcribe_with_iflytek(
    audio_file_path: str,
    language: str = "zh_cn",
    output_format: str = "txt"
) -> Dict[str, Any]:
    """
    使用讯飞API转录音频文件

    Args:
        audio_file_path: 音频文件路径
        language: 语言代码
        output_format: 输出格式

    Returns:
        转录结果字典
    """
    asr = IFlytekASR()
    return asr.transcribe_file(audio_file_path, language, output_format)
