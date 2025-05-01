import sys
import zipfile
import os
from testing import runTests

def release(zip_name):
    runTests()

    folder_path = "src"
    zip_path = f"{zip_name}.zip"

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    z.write(file_path, arcname)
    except Exception as e:
        print(f"Error occurred during zipping: {e}")
        return

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide the zip name as an argument.")
        sys.exit(1)

    zip_name = sys.argv[1]
    release(zip_name)
