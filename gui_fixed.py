"""
YouTube KOL Crawler GUI Launcher
完整功能版本 - 包含实时分析、API状态、优化进度显示
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import os
import sys
import queue
from datetime import datetime, timedelta
import json
import pytz
import re

class YouTubeCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube KOL Crawler - Professional Edition")
        self.root.geometry("1000x750")
        
        # 设置图标（如果存在）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="YouTube KOL Crawler Control Panel", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="Crawler Settings", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 关键词输入
        ttk.Label(input_frame, text="Keywords:").grid(row=0, column=0, sticky=tk.W)
        self.keywords_entry = ttk.Entry(input_frame, width=50)
        self.keywords_entry.grid(row=0, column=1, columnspan=2, padx=5)
        self.keywords_entry.insert(0, "AI technology")
        ttk.Label(input_frame, text="(Separate multiple keywords with commas)").grid(
            row=0, column=3, sticky=tk.W, padx=5)
        
        # 起始年份
        ttk.Label(input_frame, text="Start Year:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_year = tk.StringVar(value="2024")
        year_spinbox = ttk.Spinbox(input_frame, from_=2005, to=2025, 
                                   textvariable=self.start_year, width=10)
        year_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # 最大结果数
        ttk.Label(input_frame, text="Max Results:").grid(row=1, column=1, sticky=tk.E, padx=(50,5))
        self.max_results = tk.StringVar(value="0")
        max_results_entry = ttk.Entry(input_frame, textvariable=self.max_results, width=10)
        max_results_entry.grid(row=1, column=2, sticky=tk.W, padx=5)
        ttk.Label(input_frame, text="(0 = unlimited)").grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # 选项
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.estimate_only = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Estimate Cost Only", 
                       variable=self.estimate_only).grid(row=0, column=0, sticky=tk.W)
        
        self.process_queue = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Process Failed Queue", 
                       variable=self.process_queue).grid(row=0, column=1, sticky=tk.W)
        
        self.show_analysis = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Show Analysis After Crawl", 
                       variable=self.show_analysis).grid(row=0, column=2, sticky=tk.W)
        
        # API状态框架
        api_frame = ttk.LabelFrame(main_frame, text="API Status", padding="5")
        api_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.api_status_label = ttk.Label(api_frame, text="API Status: Ready", font=('Arial', 10))
        self.api_status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Crawling", 
                                      command=self.start_crawling, width=20)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_crawling, width=15, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="View Status", 
                  command=self.view_api_status, width=15).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Analyze", 
                  command=self.analyze_current_keyword, width=15).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Export Data", 
                  command=self.export_data, width=15).grid(row=0, column=4, padx=5)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="10")
        output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=18, width=120, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 右键菜单
        self.output_menu = tk.Menu(self.output_text, tearoff=0)
        self.output_menu.add_command(label="Clear", command=self.clear_output)
        self.output_menu.add_command(label="Copy All", command=self.copy_output)
        self.output_text.bind("<Button-3>", self.show_output_menu)
        
        # 进度条和统计
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=700)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=1, padx=10)
        
        # 状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.stats_label = ttk.Label(status_frame, text="", relief=tk.SUNKEN)
        self.stats_label.grid(row=0, column=1, sticky=(tk.E))
        
        status_frame.columnconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # 进程管理
        self.current_process = None
        self.output_queue = queue.Queue()
        self.current_keyword = ""
        self.crawl_stats = {}
        self.total_videos_expected = 0
        
        # 检查环境
        self.check_environment()
        
        # 启动输出监控
        self.monitor_output()
        
        # 定期更新API状态
        self.update_api_status()
    
    def check_environment(self):
        """检查环境配置"""
        self.log("[CHECK] Checking environment...")
        
        # 检查Python
        try:
            # 优先使用虚拟环境的Python
            if os.path.exists("venv\\Scripts\\python.exe"):
                result = subprocess.run(["venv\\Scripts\\python.exe", "--version"], 
                                      capture_output=True, text=True)
                self.log(f"[OK] Python (venv): {result.stdout.strip()}")
            else:
                result = subprocess.run(["python", "--version"], 
                                      capture_output=True, text=True)
                self.log(f"[OK] Python: {result.stdout.strip()}")
        except:
            self.log("[ERROR] Python not found!")
            messagebox.showerror("Error", "Python is not installed or not in PATH!")
        
        # 检查.env文件
        if os.path.exists(".env"):
            self.log("[OK] Configuration file (.env) found")
            self.check_api_keys()
        else:
            self.log("[WARNING] Configuration file (.env) not found")
            if messagebox.askyesno("Setup", "Configuration file not found. Create from template?"):
                try:
                    import shutil
                    shutil.copy(".env.example", ".env")
                    self.log("[OK] Created .env from template")
                    os.startfile(".env")
                except Exception as e:
                    self.log(f"[ERROR] Error creating .env: {e}")
        
        # 检查数据库
        if os.path.exists("data\\youtube_kol.db"):
            try:
                import sqlite3
                conn = sqlite3.connect("data\\youtube_kol.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM videos")
                video_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM channels")
                channel_count = cursor.fetchone()[0]
                conn.close()
                self.log(f"[OK] Database found: {video_count} videos, {channel_count} channels")
                self.stats_label.config(text=f"Videos: {video_count} | Channels: {channel_count}")
            except Exception as e:
                self.log(f"[OK] Database found (new/empty)")
        else:
            self.log("[INFO] Database will be created on first run")
        
        self.log("="*60)
        self.log("Ready to use! Click 'Start Crawling' to begin.")
    
    def check_api_keys(self):
        """检查API密钥配置"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            keys = os.getenv('YOUTUBE_API_KEYS', '').split(',')
            valid_keys = [k.strip() for k in keys if k.strip()]
            if valid_keys:
                self.log(f"[OK] Found {len(valid_keys)} API key(s)")
        except:
            pass
    
    def log(self, message):
        """添加日志到输出框"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_output(self):
        """清空输出"""
        self.output_text.delete(1.0, tk.END)
    
    def copy_output(self):
        """复制所有输出"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
    
    def show_output_menu(self, event):
        """显示右键菜单"""
        self.output_menu.post(event.x_root, event.y_root)
    
    def monitor_output(self):
        """监控输出队列"""
        try:
            while not self.output_queue.empty():
                message = self.output_queue.get_nowait()
                self.log(message)
                
                # 解析进度信息
                self.parse_progress(message)
                
        except:
            pass
        
        self.root.after(100, self.monitor_output)
    
    def parse_progress(self, message):
        """解析进度信息并更新显示"""
        # 解析[stats]行
        if "[stats]" in message:
            match = re.search(r'fetched=(\d+)\s+inserted=(\d+)\s+channels=(\d+)', message)
            if match:
                fetched = int(match.group(1))
                inserted = int(match.group(2))
                channels = int(match.group(3))
                
                # 更新统计
                self.crawl_stats = {
                    'fetched': fetched,
                    'inserted': inserted,
                    'channels': channels
                }
                
                # 更新状态标签
                self.stats_label.config(text=f"Fetched: {fetched} | Inserted: {inserted} | Channels: {channels}")
                
                # 更新进度条（根据实际抓取情况）
                if self.total_videos_expected > 0:
                    progress = min((fetched / self.total_videos_expected) * 100, 100)
                else:
                    # 如果没有预期值，使用插入数作为进度指示
                    if inserted > 0:
                        progress = min((inserted / max(fetched, 1)) * 100, 100)
                    else:
                        progress = 0
                
                self.progress_var.set(progress)
                self.progress_label.config(text=f"{progress:.1f}%")
        
        # 解析估算信息
        if "Estimated videos:" in message:
            match = re.search(r'Estimated videos:\s*(\d+)', message)
            if match:
                self.total_videos_expected = int(match.group(1))
                self.log(f"[Info] Expected to fetch approximately {self.total_videos_expected} videos")
        
        # 解析API状态
        if "Stats:" in message and "api_calls" in message:
            self.parse_api_usage(message)
    
    def parse_api_usage(self, message):
        """解析API使用情况"""
        try:
            # 提取API调用次数
            match = re.search(r'api_calls[:\s]+(\d+)', message)
            if match:
                api_calls = int(match.group(1))
                # 估算消耗的配额（搜索100，其他1）
                estimated_cost = api_calls * 30  # 平均估算
                self.update_api_status_with_usage(estimated_cost)
        except:
            pass
    
    def update_api_status(self):
        """定期更新API状态"""
        try:
            # 获取当前API状态
            if os.path.exists("venv\\Scripts\\python.exe"):
                python_exe = "venv\\Scripts\\python.exe"
            else:
                python_exe = "python"
            
            # 运行状态检查
            result = subprocess.run(
                [python_exe, "main.py", "--status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # 解析输出
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Total Remaining Quota:" in line:
                        match = re.search(r'Total Remaining Quota:\s*(\d+)', line)
                        if match:
                            remaining = int(match.group(1))
                            self.display_api_status(remaining)
                            break
        except:
            pass
        
        # 每30秒更新一次
        self.root.after(30000, self.update_api_status)
    
    def update_api_status_with_usage(self, used_quota):
        """更新API状态显示（带使用量）"""
        try:
            # 计算剩余配额（假设每个key 10000配额）
            from dotenv import load_dotenv
            load_dotenv()
            keys = os.getenv('YOUTUBE_API_KEYS', '').split(',')
            valid_keys = [k.strip() for k in keys if k.strip()]
            total_quota = len(valid_keys) * 10000
            remaining = max(0, total_quota - used_quota)
            self.display_api_status(remaining)
        except:
            pass
    
    def display_api_status(self, remaining_quota):
        """显示API状态和剩余配额"""
        # 获取太平洋时间和北京时间
        pacific = pytz.timezone('US/Pacific')
        beijing = pytz.timezone('Asia/Shanghai')
        
        now_pacific = datetime.now(pacific)
        now_beijing = datetime.now(beijing)
        
        # 计算到太平洋时间午夜的剩余时间（配额重置时间）
        pacific_midnight = now_pacific.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        beijing_reset_time = pacific_midnight.astimezone(beijing)
        
        hours_until_reset = (pacific_midnight - now_pacific).total_seconds() / 3600
        
        status_text = f"API Quota: {remaining_quota:,} remaining | Resets at {beijing_reset_time.strftime('%H:%M')} Beijing Time ({hours_until_reset:.1f}h)"
        self.api_status_label.config(text=status_text)
        
        # 根据剩余量改变颜色
        if remaining_quota < 1000:
            self.api_status_label.config(foreground="red")
        elif remaining_quota < 5000:
            self.api_status_label.config(foreground="orange")
        else:
            self.api_status_label.config(foreground="green")
    
    def view_api_status(self):
        """查看详细API状态"""
        self.log("[Stats] Checking API status...")
        # 修复：不传递keywords参数给--status命令
        self.run_command_async(["status", "--status"])
    
    def analyze_current_keyword(self):
        """分析当前关键词"""
        keyword = self.current_keyword or self.keywords_entry.get().strip().split(',')[0].strip()
        if keyword:
            self.log(f"[Analyze] Analyzing keyword: {keyword}")
            self.run_analysis_async(keyword)
        else:
            messagebox.showwarning("Warning", "Please enter a keyword first!")
    
    def run_analysis_async(self, keyword):
        """异步运行分析"""
        def run():
            try:
                if os.path.exists("venv\\Scripts\\python.exe"):
                    python_exe = "venv\\Scripts\\python.exe"
                else:
                    python_exe = "python"
                
                result = subprocess.run(
                    [python_exe, "analyzer.py", "keyword", keyword],
                    capture_output=True,
                    text=True
                )
                
                # 输出分析结果
                self.output_queue.put("\n" + "="*60)
                self.output_queue.put(f"[Stats] Analysis Results for '{keyword}'")
                self.output_queue.put("="*60)
                
                # 安全处理输出（避免NoneType错误）
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            self.output_queue.put(line)
                else:
                    self.output_queue.put("[WARNING] No output from analyzer")
                
                # 如果有错误输出，也显示
                if result.stderr:
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            self.output_queue.put(f"[ERROR] {line}")
                
            except Exception as e:
                self.output_queue.put(f"[ERROR] Analysis error: {str(e)}")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def run_command_async(self, command):
        """异步运行命令"""
        def run():
            try:
                # 使用虚拟环境的Python
                if os.path.exists("venv\\Scripts\\python.exe"):
                    python_exe = "venv\\Scripts\\python.exe"
                else:
                    python_exe = "python"
                
                full_command = [python_exe, "main.py"] + command
                
                self.output_queue.put(f"Running: {' '.join(full_command)}")
                
                self.current_process = subprocess.Popen(
                    full_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # 实时读取输出
                for line in iter(self.current_process.stdout.readline, ''):
                    if line:
                        line = line.strip()
                        self.output_queue.put(line)
                
                self.current_process.wait()
                
                if self.current_process.returncode == 0:
                    self.output_queue.put("[OK] Operation completed successfully!")
                    
                    # 如果启用了分析选项，自动运行分析
                    if self.show_analysis.get() and self.current_keyword and "status" not in command:
                        self.output_queue.put(f"\n[Stats] Running analysis for '{self.current_keyword}'...")
                        self.run_analysis_async(self.current_keyword)
                else:
                    self.output_queue.put(f"[WARNING] Process exited with code {self.current_process.returncode}")
                    
            except Exception as e:
                self.output_queue.put(f"[ERROR] Error: {str(e)}")
            finally:
                self.current_process = None
                self.root.after(0, self.on_command_complete)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def on_command_complete(self):
        """命令完成后的处理"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.status_label.config(text="Ready")
        
        # 显示最终的API状态
        self.update_api_status()
    
    def start_crawling(self):
        """开始爬取"""
        keywords = self.keywords_entry.get().strip()
        if not keywords:
            messagebox.showwarning("Warning", "Please enter keywords!")
            return
        
        # 保存当前关键词（用于导出）
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        self.current_keyword = keyword_list[0] if keyword_list else ""
        
        # 重置进度
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.total_videos_expected = 0
        self.crawl_stats = {}
        
        # 禁用开始按钮，启用停止按钮
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Running...")
        
        # 不再使用不确定的进度条
        # self.progress_bar.start(10)
        
        command = []
        
        # 添加关键词
        for keyword in keyword_list:
            command.append(keyword)
        
        # 添加参数
        if self.start_year.get():
            command.extend(["--start-year", self.start_year.get()])
        
        if self.max_results.get() and self.max_results.get() != "0":
            command.extend(["--max-results", self.max_results.get()])
            # 设置预期数量
            self.total_videos_expected = int(self.max_results.get())
        
        if self.estimate_only.get():
            command.append("--estimate-only")
        
        if self.process_queue.get():
            command.append("--process-queue")
        
        self.log(f"[START] Starting crawler for keywords: {', '.join(keyword_list)}")
        self.run_command_async(command)
    
    def stop_crawling(self):
        """停止爬取"""
        if self.current_process:
            self.current_process.terminate()
            self.log("[STOP] Stopping crawler...")
            self.stop_button.config(state='disabled')
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
    
    def export_data(self):
        """导出数据 - 使用当前关键词"""
        # 创建导出窗口
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Data")
        export_window.geometry("450x300")
        
        # 主框架
        frame = ttk.Frame(export_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Export Data to File", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Keyword:").grid(row=1, column=0, sticky=tk.W, pady=5)
        keyword_var = tk.StringVar(value=self.current_keyword)
        keyword_entry = ttk.Entry(frame, textvariable=keyword_var, width=30)
        keyword_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Format:").grid(row=2, column=0, sticky=tk.W, pady=5)
        format_var = tk.StringVar(value="excel")
        format_combo = ttk.Combobox(frame, textvariable=format_var, 
                                    values=["excel", "csv", "json"], 
                                    state="readonly", width=28)
        format_combo.grid(row=2, column=1, pady=5)
        
        # 添加导出选项
        export_all_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Export all data (ignore keyword)", 
                       variable=export_all_var).grid(row=3, column=0, columnspan=2, pady=10)
        
        def run_export():
            format_type = format_var.get()
            
            if export_all_var.get():
                self.log(f"[Export] Exporting all data to {format_type.upper()}...")
                keyword = ""
            else:
                keyword = keyword_var.get().strip()
                if keyword:
                    self.log(f"[Export] Exporting data for '{keyword}' to {format_type.upper()}...")
                else:
                    self.log(f"[Export] Exporting all data to {format_type.upper()}...")
            
            # 使用虚拟环境的Python
            if os.path.exists("venv\\Scripts\\python.exe"):
                python_exe = "venv\\Scripts\\python.exe"
            else:
                python_exe = "python"
            
            cmd = [python_exe, "analyzer.py", "export", "--format", format_type]
            if keyword and not export_all_var.get():
                cmd.extend(["--keyword", keyword])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"[OK] Export completed successfully!")
                    # 打开data文件夹
                    os.startfile("data")
                else:
                    self.log(f"[ERROR] Export failed: {result.stderr}")
            except Exception as e:
                self.log(f"[ERROR] Export error: {str(e)}")
            
            export_window.destroy()
        
        ttk.Button(frame, text="Export", command=run_export, width=20).grid(
            row=4, column=0, columnspan=2, pady=20)
        
        export_window.columnconfigure(0, weight=1)
        export_window.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

def main():
    root = tk.Tk()
    app = YouTubeCrawlerGUI(root)
    
    # 处理窗口关闭
    def on_closing():
        if app.current_process:
            if messagebox.askokcancel("Quit", "A process is running. Do you want to stop it and quit?"):
                app.current_process.terminate()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        if app.current_process:
            app.current_process.terminate()
        root.destroy()

if __name__ == "__main__":
    main()
