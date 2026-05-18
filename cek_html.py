import os

path_target = r"D:\APPS\Project\lumra\lumra_config"
output_file = "daftar_html.md"

with open(output_file, "w") as f:
    f.write("# Daftar File HTML\n\n")
    f.write("| No | Nama File | Path |\n")
    f.write("|---|---|---|\n")
    
    count = 1
    for root, dirs, files in os.walk(path_target):
        for file in files:
            if file.endswith(".html"):
                f.write(f"| {count} | {file} | {root} |\n")
                count += 1