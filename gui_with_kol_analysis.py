"""
YouTube KOL Crawler GUI - 增强版（包含KOL分析功能）
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
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="YouTube KOL Crawler Control Panel", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="Crawler Settings", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(input_frame, text="Keywords:").grid(row=0, column=0, sticky=tk.W)
        self.keywords_entry = ttk.Entry(input_frame, width=50)
        self.keywords_entry.grid(row=0, column=1, columnspan=2, padx=5)
        self.keywords_entry.insert(0, "AI technology")
        ttk.Label(input_frame, text="(Separate multiple keywords with commas)").grid(
            row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(input_frame, text="Start Year:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_year = tk.StringVar(value="2024")
        year_spinbox = ttk.Spinbox(input_frame, from_=2005, to=2025, 
                                   textvariable=self.start_year, width=10)
        year_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5)
        
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
        
        # API状态
        api_frame = ttk.LabelFrame(main_frame, text="API Status", padding="5")
        api_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.api_status_label = ttk.Label(api_frame, text="API Status: Ready", font=('Arial', 10))
        self.api_status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 按钮区域 - 添加KOL分析按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Crawling", 
                                      command=self.start_crawling, width=15)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_crawling, width=12, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="View Status", 
                  command=self.view_api_status, width=12).grid(row=0, column=2, padx=5)
        
        # 🆕 新增：KOL分析按钮
        self.kol_analyze_button = ttk.Button(button_frame, text="🎯 KOL Analysis", 
                  command=self.show_kol_analysis_dialog, width=15, 
                  style='Accent.TButton')
        self.kol_analyze_button.grid(row=0, column=3, padx=5)
        
        ttk.Button(button_frame, text="Analyze", 
                  command=self.analyze_current_keyword, width=12).grid(row=0, column=4, padx=5)
        ttk.Button(button_frame, text="Export Data", 
                  command=self.export_data, width=12).grid(row=0, column=5, padx=5)
        
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
        
        # 进度条
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
        
        # 配置网格
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
        
        self.check_environment()
        self.monitor_output()
        self.update_api_status()
    
    # 🆕 新增：KOL分析对话框
    def show_kol_analysis_dialog(self):
        """显示KOL分析配置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("KOL Analysis")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="🎯 YouTube KOL Analysis", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Keyword:").grid(row=1, column=0, sticky=tk.W, pady=5)
        keyword_var = tk.StringVar(value=self.current_keyword or self.keywords_entry.get().strip().split(',')[0].strip())
        keyword_entry = ttk.Entry(frame, textvariable=keyword_var, width=35)
        keyword_entry.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # 分析选项
        options_frame = ttk.LabelFrame(frame, text="Analysis Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        db_only_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(options_frame, text="从数据库分析（快速，不消耗API）", 
                       variable=db_only_var, value=True).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(options_frame, text="完整分析（包括爬取新数据）", 
                       variable=db_only_var, value=False).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        get_latest_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="获取每个频道最新10个视频（消耗API配额）", 
                       variable=get_latest_var).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # 说明文字
        info_frame = ttk.Frame(frame)
        info_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        info_text = tk.Text(info_frame, height=6, width=55, wrap=tk.WORD, 
                          bg='#f0f0f0', relief=tk.FLAT, font=('Arial', 9))
        info_text.insert('1.0', 
            "💡 说明：\n"
            "• 从数据库分析：使用已爬取的数据，速度快\n"
            "• 完整分析：先爬取最新数据，再分析\n"
            "• 获取最新视频：为每个频道调用API获取最新内容\n"
            "  （注意：100个频道约消耗10,000 API配额）\n"
            "\n结果将生成包含3个Sheet的Excel文件"
        )
        info_text.config(state='disabled')
        info_text.grid(row=0, column=0)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        def start_analysis():
            keyword = keyword_var.get().strip()
            if not keyword:
                messagebox.showwarning("Warning", "请输入关键词！")
                return
            
            dialog.destroy()
            self.run_kol_analysis(keyword, db_only_var.get(), get_latest_var.get())
        
        ttk.Button(button_frame, text="开始分析", command=start_analysis, 
                  width=20).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy, 
                  width=15).grid(row=0, column=1, padx=5)
        
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
    
    # 🆕 新增：运行KOL分析
    def run_kol_analysis(self, keyword, db_only=True, get_latest=False):
        """运行KOL分析"""
        self.log("="*60)
        self.log(f"🎯 [KOL Analysis] 开始分析关键词: {keyword}")
        self.log("="*60)
        
        if db_only:
            self.log("[Info] 模式: 从数据库分析（快速）")
        else:
            self.log("[Info] 模式: 完整分析（包括爬取）")
        
        if get_latest:
            self.log("[Info] 将获取每个频道最新10个视频（消耗API配额）")
        
        self.status_label.config(text="KOL Analysis Running...")
        self.kol_analyze_button.config(state='disabled')
        self.progress_bar.start(10)
        
        def run():
            try:
                if os.path.exists("venv\\Scripts\\python.exe"):
                    python_exe = "venv\\Scripts\\python.exe"
                else:
                    python_exe = "python"
                
                # 构建命令
                cmd = [python_exe, "analyze_keyword_kol.py", keyword]
                
                if db_only:
                    cmd.append("--db-only")
                else:
                    if self.start_year.get():
                        cmd.extend(["--start-year", self.start_year.get()])
                
                if get_latest:
                    cmd.append("--get-latest-videos")
                
                self.output_queue.put(f"[CMD] {' '.join(cmd)}")
                
                # 运行分析
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # 实时输出
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.output_queue.put(line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.output_queue.put("")
                    self.output_queue.put("="*60)
                    self.output_queue.put("✅ [SUCCESS] KOL分析完成！")
                    self.output_queue.put("="*60)
                    self.output_queue.put("")
                    self.output_queue.put("📊 结果文件已生成在 data 目录")
                    self.output_queue.put("💡 提示：双击打开 Excel 文件查看详细分析")
                    self.output_queue.put("")
                    
                    # 自动打开data文件夹
                    self.root.after(1000, lambda: self.open_data_folder())
                else:
                    self.output_queue.put(f"❌ [ERROR] 分析失败，退出码: {process.returncode}")
                
            except Exception as e:
                self.output_queue.put(f"❌ [ERROR] {str(e)}")
            finally:
                self.root.after(0, self.on_kol_analysis_complete)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def on_kol_analysis_complete(self):
        """KOL分析完成后的处理"""
        self.status_label.config(text="Ready")
        self.kol_analyze_button.config(state='normal')
        self.progress_bar.stop()
        self.progress_var.set(0)
    
    def open_data_folder(self):
        """打开data文件夹"""
        try:
            if os.path.exists("data"):
                os.startfile("data")
        except:
            pass
    
    # [以下是原有方法，保持不变]
    def check_environment(self):
        self.log("[CHECK] Checking environment...")
        try:
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
        
        if os.path.exists(".env"):
            self.log("[OK] Configuration file (.env) found")
            self.check_api_keys()
        else:
            self.log("[WARNING] Configuration file (.env) not found")
        
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
            except:
                self.log(f"[OK] Database found (new/empty)")
        
        self.log("="*60)
        self.log("Ready to use! Click 'Start Crawling' or 'KOL Analysis'")
    
    def check_api_keys(self):
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
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
    
    def copy_output(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
    
    def show_output_menu(self, event):
        self.output_menu.post(event.x_root, event.y_root)
    
    def monitor_output(self):
        try:
            while not self.output_queue.empty():
                message = self.output_queue.get_nowait()
                self.log(message)
                self.parse_progress(message)
        except:
            pass
        self.root.after(100, self.monitor_output)
    
    def parse_progress(self, message):
        if "[stats]" in message:
            match = re.search(r'fetched=(\d+)\s+inserted=(\d+)\s+channels=(\d+)', message)
            if match:
                fetched, inserted, channels = int(match.group(1)), int(match.group(2)), int(match.group(3))
                self.crawl_stats = {'fetched': fetched, 'inserted': inserted, 'channels': channels}
                self.stats_label.config(text=f"Fetched: {fetched} | Inserted: {inserted} | Channels: {channels}")
                if self.total_videos_expected > 0:
                    progress = min((fetched / self.total_videos_expected) * 100, 100)
                else:
                    progress = min((inserted / max(fetched, 1)) * 100, 100) if inserted > 0 else 0
                self.progress_var.set(progress)
                self.progress_label.config(text=f"{progress:.1f}%")
    
    def update_api_status(self):
        try:
            python_exe = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else "python"
            result = subprocess.run([python_exe, "main.py", "--status"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "Total Remaining Quota:" in line:
                        match = re.search(r'Total Remaining Quota:\s*(\d+)', line)
                        if match:
                            self.display_api_status(int(match.group(1)))
                            break
        except:
            pass
        self.root.after(30000, self.update_api_status)
    
    def display_api_status(self, remaining_quota):
        pacific = pytz.timezone('US/Pacific')
        beijing = pytz.timezone('Asia/Shanghai')
        now_pacific, now_beijing = datetime.now(pacific), datetime.now(beijing)
        pacific_midnight = now_pacific.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        beijing_reset = pacific_midnight.astimezone(beijing)
        hours_until = (pacific_midnight - now_pacific).total_seconds() / 3600
        
        status_text = f"API Quota: {remaining_quota:,} remaining | Resets at {beijing_reset.strftime('%H:%M')} Beijing Time ({hours_until:.1f}h)"
        self.api_status_label.config(text=status_text)
        
        color = "red" if remaining_quota < 1000 else "orange" if remaining_quota < 5000 else "green"
        self.api_status_label.config(foreground=color)
    
    def view_api_status(self):
        self.log("[Stats] Checking API status...")
        self.run_command_async(["--status"])
    
    def analyze_current_keyword(self):
        keyword = self.current_keyword or self.keywords_entry.get().strip().split(',')[0].strip()
        if keyword:
            self.log(f"[Analyze] Analyzing keyword: {keyword}")
            self.run_analysis_async(keyword)
        else:
            messagebox.showwarning("Warning", "Please enter a keyword first!")
    
    def run_analysis_async(self, keyword):
        def run():
            try:
                python_exe = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else "python"
                result = subprocess.run([python_exe, "analyzer.py", "keyword", keyword], capture_output=True, text=True)
                self.output_queue.put("\n" + "="*60)
                self.output_queue.put(f"[Stats] Analysis Results for '{keyword}'")
                self.output_queue.put("="*60)
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            self.output_queue.put(line)
                if result.stderr:
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            self.output_queue.put(f"[ERROR] {line}")
            except Exception as e:
                self.output_queue.put(f"[ERROR] {str(e)}")
        threading.Thread(target=run, daemon=True).start()
    
    def run_command_async(self, command):
        def run():
            try:
                python_exe = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else "python"
                full_command = [python_exe, "main.py"] + command
                self.output_queue.put(f"Running: {' '.join(full_command)}")
                
                self.current_process = subprocess.Popen(full_command, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
                
                for line in iter(self.current_process.stdout.readline, ''):
                    if line:
                        self.output_queue.put(line.strip())
                
                self.current_process.wait()
                
                if self.current_process.returncode == 0:
                    self.output_queue.put("[OK] Operation completed successfully!")
                    if self.show_analysis.get() and self.current_keyword and "--status" not in command:
                        self.output_queue.put(f"\n[Stats] Running analysis for '{self.current_keyword}'...")
                        self.run_analysis_async(self.current_keyword)
                else:
                    self.output_queue.put(f"[WARNING] Process exited with code {self.current_process.returncode}")
            except Exception as e:
                self.output_queue.put(f"[ERROR] {str(e)}")
            finally:
                self.current_process = None
                self.root.after(0, self.on_command_complete)
        threading.Thread(target=run, daemon=True).start()
    
    def on_command_complete(self):
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.status_label.config(text="Ready")
        self.update_api_status()
    
    def start_crawling(self):
        keywords = self.keywords_entry.get().strip()
        if not keywords:
            messagebox.showwarning("Warning", "Please enter keywords!")
            return
        
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        self.current_keyword = keyword_list[0] if keyword_list else ""
        
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.total_videos_expected = 0
        self.crawl_stats = {}
        
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Running...")
        
        command = []
        for keyword in keyword_list:
            command.append(keyword)
        
        if self.start_year.get():
            command.extend(["--start-year", self.start_year.get()])
        if self.max_results.get() and self.max_results.get() != "0":
            command.extend(["--max-results", self.max_results.get()])
            self.total_videos_expected = int(self.max_results.get())
        if self.estimate_only.get():
            command.append("--estimate-only")
        if self.process_queue.get():
            command.append("--process-queue")
        
        self.log(f"[START] Starting crawler for keywords: {', '.join(keyword_list)}")
        self.run_command_async(command)
    
    def stop_crawling(self):
        if self.current_process:
            self.current_process.terminate()
            self.log("[STOP] Stopping crawler...")
            self.stop_button.config(state='disabled')
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
    
    def export_data(self):
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Data")
        export_window.geometry("450x300")
        
        frame = ttk.Frame(export_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Export Data to File", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Keyword:").grid(row=1, column=0, sticky=tk.W, pady=5)
        keyword_var = tk.StringVar(value=self.current_keyword)
        ttk.Entry(frame, textvariable=keyword_var, width=30).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Format:").grid(row=2, column=0, sticky=tk.W, pady=5)
        format_var = tk.StringVar(value="excel")
        ttk.Combobox(frame, textvariable=format_var, values=["excel", "csv", "json"], 
                    state="readonly", width=28).grid(row=2, column=1, pady=5)
        
        export_all_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Export all data", variable=export_all_var).grid(row=3, column=0, columnspan=2, pady=10)
        
        def run_export():
            python_exe = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else "python"
            cmd = [python_exe, "analyzer.py", "export", "--format", format_var.get()]
            keyword = keyword_var.get().strip()
            if keyword and not export_all_var.get():
                cmd.extend(["--keyword", keyword])
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("[OK] Export completed!")
                    os.startfile("data")
                else:
                    self.log(f"[ERROR] Export failed")
            except Exception as e:
                self.log(f"[ERROR] {str(e)}")
            export_window.destroy()
        
        ttk.Button(frame, text="Export", command=run_export, width=20).grid(row=4, column=0, columnspan=2, pady=20)
        
        export_window.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

def main():
    root = tk.Tk()
    app = YouTubeCrawlerGUI(root)
    
    def on_closing():
        if app.current_process:
            if messagebox.askokcancel("Quit", "A process is running. Stop and quit?"):
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
