#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import config
import time

def generate_error_svg(error_type, session_log_path):
    # Error code definitions
    error_messages = {
        "1": "Unknown Error / 未知错误",
        "2": "Weather API Request Failed / 天气请求失败",
        "3": "Coordinates Not Set / 经纬度未设置",
        "4": "Wi-Fi Connection Failed / Wi-Fi 连接失败",
        "255": "Script Crashed / 脚本异常退出"
    }
    msg = error_messages.get(str(error_type), "System Error / 系统错误")

    # Read session log if debug mode is enabled
    session_log =[]
    if getattr(config, 'debug', False):
        try:
            with open(session_log_path, 'r') as f:
                # Keep the last 20 lines to fit within the screen height after wrapping
                session_log = f.readlines()[-20:]
        except Exception:
            session_log = ["Could not read session log."]

    # SVG layout settings
    # Screen size assumed to be 800x600 (landscape mode)
    svg_header = '<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" font-family="Sarasa Gothic SC, sans-serif">'
    
    # Base error icon (Circle with an 'X')
    icon_svg = '''
    <g id="icon_x" stroke="black" stroke-width="4" fill="none">
        <circle cx="0" cy="0" r="40" />
        <line x1="-20" y1="-20" x2="20" y2="20" />
        <line x1="20" y1="-20" x2="-20" y2="20" />
    </g>
    '''

    content = ""
    if not getattr(config, 'debug', False):
        # --- Minimalist Mode (Centered) ---
        # Scale icon by 1.5x and place slightly above center
        content += f'<g transform="translate(400, 200) scale(1.5)">{icon_svg}</g>'
        
        # Place text with proper spacing below the enlarged icon
        content += f'<text x="400" y="340" font-size="36" text-anchor="middle" font-weight="bold">{msg}</text>'
        content += f'<text x="400" y="400" font-size="20" text-anchor="middle" fill="gray">Time: {time.strftime("%Y-%m-%d %H:%M:%S")}</text>'
    
    else:
        # --- Debug Mode (Top Header + Log Output) ---
        
        # 1. Header Area (Top 1/6 of screen)
        # Scale down icon and align left
        content += f'<g transform="translate(50, 50) scale(0.6)">{icon_svg}</g>'
        content += f'<text x="90" y="60" font-size="24" font-weight="bold">{msg}</text>'
        
        # Horizontal separator line
        content += '<line x1="0" y1="100" x2="800" y2="100" stroke="black" stroke-width="2" />'
        
        # 2. Log Area
        content += '<text x="10" y="125" font-size="14" fill="gray" font-weight="bold">DEBUG SESSION LOG:</text>'
        
        y_pos = 150
        line_height = 22
        max_chars_per_line = 100 
        
        for line in session_log:
            line = line.strip()
            if not line: 
                continue
            
            # Escape XML special characters to prevent SVG rendering issues
            safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Text wrapping logic for long log entries (e.g., URLs)
            while len(safe_line) > 0:
                chunk = safe_line[:max_chars_per_line]
                
                # Prevent drawing text beyond the screen's bottom edge
                if y_pos > 590:
                    break
                    
                content += f'<text x="10" y="{y_pos}" font-size="16" xml:space="preserve">{chunk}</text>'
                
                safe_line = safe_line[max_chars_per_line:]
                y_pos += line_height

    svg_full = f'{svg_header}{content}</svg>'
    
    # Write output SVG
    with open("weather-script-output.svg", "w") as f:
        f.write(svg_full)

if __name__ == "__main__":
    # Expects status code and log path from command line arguments
    err_code = sys.argv[1] if len(sys.argv) > 1 else "1"
    log_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/weather_session.log"
    generate_error_svg(err_code, log_path)