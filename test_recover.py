import sys
import string

def extract_strings(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    
    printable = set(string.printable.encode('ascii'))
    strings_list = []
    current = bytearray()
    
    for b in data:
        if b in printable:
            current.append(b)
        else:
            if len(current) >= 6:
                try:
                    strings_list.append(current.decode('ascii', errors='ignore'))
                except Exception:
                    pass
            current = bytearray()
            
    if len(current) >= 6:
        try:
            strings_list.append(current.decode('ascii', errors='ignore'))
        except Exception:
            pass
            
    return strings_list

if __name__ == "__main__":
    pb_path = "/Users/COYASS/.gemini/antigravity/conversations/10257e12-b6f4-4488-be18-4d7537e274e8.pb"
    print(f"Reading {pb_path}...")
    extracted = extract_strings(pb_path)
    
    # "class ContentGenerator" などのキーワードで絞り込む
    print("Searching for definitions...")
    for idx, s in enumerate(extracted):
        if "ContentGenerator" in s or "generator.py" in s or "fact_checker.py" in s:
            print(f"\n--- Match {idx} ---")
            # 周囲の文字列も少し表示する
            start = max(0, idx - 5)
            end = min(len(extracted), idx + 10)
            for i in range(start, end):
                print(extracted[i])
