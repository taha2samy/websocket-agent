import asyncio
import websockets
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading

class WebSocketClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WebSocket TTK Client")
        
        # GUI elements
        self.setup_gui()
        
        # WebSocket connection
        self.websocket = None
        # Create a new event loop for background tasks
        self.loop = asyncio.new_event_loop()
        
        # Start a background thread for the asyncio loop
        threading.Thread(target=self.run_event_loop, daemon=True).start()

    def run_event_loop(self):
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def setup_gui(self):
        # Header Section
        headers_frame = ttk.LabelFrame(self.root, text="Headers", padding=(10, 10))
        headers_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ttk.Label(headers_frame, text="Token:").grid(row=0, column=0, sticky="w")
        self.token_entry = ttk.Entry(headers_frame, width=30)
        self.token_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(headers_frame, text="Tags (comma-separated):").grid(row=1, column=0, sticky="w")
        self.tag_entry = ttk.Entry(headers_frame, width=30)
        self.tag_entry.grid(row=1, column=1, padx=5, pady=5)

        # Connection Button
        self.connect_button = ttk.Button(headers_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Message Section
        message_frame = ttk.LabelFrame(self.root, text="Message", padding=(10, 10))
        message_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        ttk.Label(message_frame, text="Enter Message:").grid(row=0, column=0, sticky="w")
        self.message_entry = ttk.Entry(message_frame, width=40)
        self.message_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.send_button = ttk.Button(message_frame, text="Send Message", command=self.send_message, state="disabled")
        self.send_button.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Received Messages Section
        received_frame = ttk.LabelFrame(self.root, text="Received Messages", padding=(10, 10))
        received_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.received_text = scrolledtext.ScrolledText(received_frame, width=50, height=10, state='disabled')
        self.received_text.grid(row=0, column=0, padx=5, pady=5)

    async def connect(self):
        headers = {
            "Authorization": self.token_entry.get(),
            "tag": self.tag_entry.get()
        }
        try:
            self.websocket = await websockets.connect("ws://localhost:8765", extra_headers=headers)
            self.connect_button.config(state="disabled")
            self.send_button.config(state="normal")
            await self.receive_messages()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to the server: {e}")

    def connect_to_server(self):
        # Schedule the connect coroutine to run in the event loop
        asyncio.run_coroutine_threadsafe(self.connect(), self.loop)

    async def receive_messages(self):
        try:
            while True:
                message = await self.websocket.recv()
                self.received_text.config(state='normal')
                self.received_text.insert(tk.END, f"Received: {message}\n")
                self.received_text.config(state='disabled')
                self.received_text.yview(tk.END)
        except websockets.ConnectionClosed:
            messagebox.showinfo("Disconnected", "Connection closed by the server.")
            self.connect_button.config(state="normal")
            self.send_button.config(state="disabled")

    async def send(self):
        message = self.message_entry.get()
        if self.websocket and message:
            await self.websocket.send(message)
            self.message_entry.delete(0, tk.END)

    def send_message(self):
        # Schedule the send coroutine to run in the event loop
        asyncio.run_coroutine_threadsafe(self.send(), self.loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebSocketClientApp(root)
    root.mainloop()
