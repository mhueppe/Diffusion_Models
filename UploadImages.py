from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
from multiprocessing import Process, Value
from threading import Thread
from preprocessing.preprocessing_webscraping_all import distribute
def uploadFiles(drive, parent_id, files, count, total, name):
    for file in files:
        gfile = drive.CreateFile({'parents': [
            {'id': parent_id}]})  # Read file and set it as the content of this instance.
        gfile.SetContentFile(file)
        gfile.Upload()  # Upload the file.
        print(f"{count.value} / {total} Uploaded: {file}. from {name}")
        count.value += 1

def uploadFolder(raw_path, parent_name, parent_id, count, total):
    gauth = GoogleAuth(settings_file=r"C:\Users\mhuep\Master_Informatik\Semester_1\Bio_inspired_AI\Diffusion_Models\settings.yaml")
    drive = GoogleDrive(gauth)
    dir_path = os.path.join(raw_path, parent_name)
    files = os.listdir(dir_path)
    os.chdir(dir_path)
    groups = distribute(files, 10)
    uploadThreads = []
    for i, group in enumerate(groups):
        uploadThread = Thread(target=uploadFiles, args=(drive, parent_id, group, count, total, parent_name+"_"+str(i)))
        uploadThread.start()
        uploadThreads.append(uploadThread)

    for t in uploadThreads:

        t.join()

def create_folder(drive, parent_id, folder_name):
    folder_metadata = {
        'title': folder_name,
        'parents': [{'kind': 'drive#fileLink', 'id': parent_id}],
        'mimeType': 'application/vnd.google-apps.folder'
    }

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()

    print(f'Folder created: {folder["id"]}')
    return folder['id']

if __name__ == '__main__':
    gauth = GoogleAuth(settings_file=r"C:\Users\mhuep\Master_Informatik\Semester_1\Bio_inspired_AI\Diffusion_Models\settings.yaml")
    drive = GoogleDrive(gauth)
    upload_file_list = [r"C:\Users\mhuep\Master_Informatik\Semester_1\Bio_inspired_AI\Diffusion_Models\preprocessing\data\raw\Body01\artwork_alt_large_rolycoly_alt.png"]
    raw_path = r"C:\Users\mhuep\Master_Informatik\Semester_1\Bio_inspired_AI\Diffusion_Models\preprocessing\data\raw"
    bodyTypes = os.listdir(raw_path)
    files_per_bodyType = {bodyType: os.listdir(os.path.join(raw_path, bodyType)) for bodyType in bodyTypes}
    bodyType_to_id = {}
    total = 0
    for files in files_per_bodyType.values():
        total += len(files)
    c = Value("i", 0)

    processes = []
    for bodyType in bodyTypes:
        id = create_folder(drive, "1I1BUHqcrWsdLBQ6CGvUnegjMSrPYmyI8", bodyType)
        uploadProcess = Process(target=uploadFolder, args=(raw_path, bodyType, id, c, total))
        uploadProcess.start()
        processes.append(uploadProcess)

    for p in processes:
        p.join()
