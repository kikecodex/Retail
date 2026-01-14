import ftplib
import os

# FTP Credentials
FTP_HOST = "inkalegacy.com"
FTP_USER = "inkalegacy"
FTP_PASS = "eCanEipRWaQHz54U"
FTP_DIR = "/public_html"

def upload_files():
    try:
        # Connect to FTP
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print(f"Connected to {FTP_HOST}")

        # Navigate to directory
        ftp.cwd(FTP_DIR)
        print(f"Changed directory to {FTP_DIR}")

        # Files to upload
        files = [
            ("index.html", "index.html")
        ]

        for local_file, remote_file in files:
            if os.path.exists(local_file):
                with open(local_file, "rb") as f:
                    print(f"Uploading {local_file}...")
                    ftp.storbinary(f"STOR {remote_file}", f)
                    print(f"Uploaded {local_file} successfully.")
            else:
                print(f"File {local_file} not found locally.")

        ftp.quit()
        print("FTP upload completed.")

    except Exception as e:
        print(f"Error during FTP upload: {e}")

if __name__ == "__main__":
    upload_files()
