import os
import re

dir_path = "C:/Users/wolff/Documents/SDKVita/Dome Keeper.v5.0.4/GOGVersion_1.4.1/ExtractPCK"

for root, _, files in os.walk(dir_path):
    for filename in files:
        if filename.endswith(".tscn") or filename.endswith(".gd") or filename.endswith(".tres"):
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if "HighlightShader.material" in content:
                    content = content.replace("HighlightShader.material", "HighlightShader.tres")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Updated {filename}")
            except Exception as e:
                pass
print("Done renaming references.")
