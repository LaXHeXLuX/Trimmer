import sys
import zipfile
import os
from testing import runTests, testMetadataMatching

def release(zip_name, test = True):
    runTests()
    if not test:
        testMetadataMatching()

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
    test = False
    if len(sys.argv) >= 3:
        test = sys.argv[2] in ['-T', '-t']
    release(zip_name, test)
