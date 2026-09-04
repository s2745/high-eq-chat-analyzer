# -*- coding: utf-8 -*-
import os
import sys
import io
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from openai import OpenAI

# ====== 编码补丁 ======
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ["PYTHONIOENCODING"] = "utf-8"

# ====== 核心逻辑类 ======
class ChatAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高情商聊天分析器")
        self.root.geometry("700x650")
        self.root.minsize(600, 500)
        
        # 状态变量
        self.api_key = None
        self.client = None
        self.context = ""
        self.chat_history = []
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # ------ 顶部：API Key 输入（首次启动） ------
        key_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=5)
        key_frame.pack(fill=tk.X)
        
        tk.Label(key_frame, text="🔑 API Key:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.key_entry = tk.Entry(key_frame, width=50, show="*")
        self.key_entry.pack(side=tk.LEFT, padx=5)
        self.key_entry.insert(0, "sk-...粘贴你的Key")
        self.key_entry.bind("<FocusIn>", lambda e: self.key_entry.delete(0, tk.END) if self.key_entry.get() == "sk-...粘贴你的Key" else None)
        
        self.connect_btn = tk.Button(key_frame, text="连接", command=self.connect_api, bg="#4CAF50", fg="white")
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(key_frame, text="⚪ 未连接", bg="#f0f0f0", fg="gray")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # ------ 背景输入 ------
        bg_frame = tk.Frame(self.root, padx=10, pady=5)
        bg_frame.pack(fill=tk.X)
        tk.Label(bg_frame, text="📝 关系背景：").pack(side=tk.LEFT)
        self.context_entry = tk.Entry(bg_frame, width=50)
        self.context_entry.pack(side=tk.LEFT, padx=5)
        self.context_entry.insert(0, "例如：平时互损的情侣 / 刚认识的朋友")
        self.context_entry.bind("<FocusIn>", lambda e: self.context_entry.delete(0, tk.END) if self.context_entry.get() == "例如：平时互损的情侣 / 刚认识的朋友" else None)
        
        # ------ 聊天记录显示区（对话历史） ------
        history_frame = tk.LabelFrame(self.root, text="💬 对话历史", padx=10, pady=5)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, height=12, font=("微软雅黑", 10), wrap=tk.WORD, state=tk.DISABLED)
        self.history_text.pack(fill=tk.BOTH, expand=True)
        # 设置历史文本颜色（用户消息蓝色，AI消息绿色）
        self.history_text.tag_config("user", foreground="#1a73e8")
        self.history_text.tag_config("ai", foreground="#0d7a3e")
        
        # ------ 用户输入区域 ------
        input_frame = tk.Frame(self.root, padx=10, pady=5)
        input_frame.pack(fill=tk.X)
        
        tk.Label(input_frame, text="你：").pack(side=tk.LEFT)
        self.user_input = tk.Entry(input_frame, width=50)
        self.user_input.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", lambda e: self.send_message())
        
        self.send_btn = tk.Button(input_frame, text="发送", command=self.send_message, bg="#1a73e8", fg="white")
        self.send_btn.pack(side=tk.LEFT, padx=5)
        
        # ------ 状态栏 ------
        self.status_bar = tk.Label(self.root, text="💡 请先点击「连接」验证 API Key", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def connect_api(self):
        """验证并连接 API"""
        key = self.key_entry.get().strip()
        if not key.startswith("sk-"):
            messagebox.showerror("错误", "API Key 格式错误，请以 'sk-' 开头")
            return
        
        try:
            self.client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
            # 测试连接：发一条极简单的消息
            test = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5
            )
            self.api_key = key
            self.status_label.config(text="✅ 已连接", fg="green")
            self.status_bar.config(text="✅ API 连接成功，可以开始分析了")
            self.key_entry.config(state=tk.DISABLED)
            self.connect_btn.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("连接失败", f"请检查网络和Key是否正确\n错误：{e}")
            self.status_label.config(text="❌ 连接失败", fg="red")
            self.status_bar.config(text="❌ API 连接失败，请重新检查 Key")
    
    def send_message(self):
        """发送用户消息并调用 AI 分析"""
        if not self.client:
            messagebox.showwarning("未连接", "请先点击「连接」验证 API Key")
            return
        
        user_msg = self.user_input.get().strip()
        if not user_msg:
            return
        
        context = self.context_entry.get().strip()
        if context == "例如：平时互损的情侣 / 刚认识的朋友" or not context:
            context = "未提供"
        
        # 显示用户消息到历史区
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"你：{user_msg}\n", "user")
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
        
        self.user_input.delete(0, tk.END)
        self.status_bar.config(text="⏳ AI 分析中，请稍候...")
        self.root.update()
        
        # 调用 API
        try:
            # 构建消息历史（简化版，保留最近10轮）
            messages = [{"role": "system", "content": self.get_system_prompt()}]
            # 从历史中提取最近对话（最多20条）
            history_lines = self.history_text.get("1.0", tk.END).strip().split("\n")
            for line in history_lines[-20:]:
                if line.startswith("你："):
                    messages.append({"role": "user", "content": line[2:]})
                elif line.startswith("AI："):
                    messages.append({"role": "assistant", "content": line[3:]})
            
            # 加上当前背景
            messages.append({"role": "user", "content": f"【背景】{context}\n【当前输入】{user_msg}"})
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.8
            )
            result = response.choices[0].message.content
            
            # 显示 AI 回复
            self.history_text.config(state=tk.NORMAL)
            self.history_text.insert(tk.END, f"AI：{result}\n\n", "ai")
            self.history_text.config(state=tk.DISABLED)
            self.history_text.see(tk.END)
            
            self.status_bar.config(text="✅ 分析完成")
        except Exception as e:
            messagebox.showerror("分析出错", f"调用 AI 失败：{e}")
            self.status_bar.config(text="❌ 分析出错")
    
    def get_system_prompt(self):
        return """
你是社交关系专家。根据背景和聊天记录，输出简洁的分析（每条不超过3行）：

【1. 语境判定】说明这是"打情骂俏"、"严肃冲突"还是"日常闲聊"。
【2. 风险扫描】若对方在PUA、钓鱼或打压，请指出；若安全，写"安全，无风险"。
【3. 对方真实状态】用一句话说透对方此刻的潜台词。
【4. 给你的回应建议】只提供1条最合适的回复话术（直接写出你可以复制粘贴去发的那句话）。

附加规则：如果用户表达了烦恼或喜悦，在最后附加一句真诚的安慰或祝福。
"""

# ====== 启动 ======
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatAnalyzerApp(root)
    root.mainloop()
