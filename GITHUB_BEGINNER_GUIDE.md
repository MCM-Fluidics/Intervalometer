# Beginner Guide: Build the APK on GitHub

You do not need to understand Python or Android build tools for this method.

## 1. Prepare the files

Upload these items from the `Intervalometer` folder:

```text
.github/workflows/build-apk.yml
buildozer.spec
main.py
README.md
requirements.txt
.gitignore
```

The `.github` folder is important. It contains the automatic APK builder.

Do not upload these local-only items:

```text
.venv/
.venv-linux/
__pycache__/
test.txt
```

## 2. Create a GitHub account

Go to https://github.com and create an account if needed. Verify the email address.

## 3. Create an empty repository

1. Click the **+** button in the top-right corner.
2. Choose **New repository**.
3. Enter a name such as `night-intervalometer`.
4. Choose **Private** unless you want the code to be public.
5. Leave **Add a README file** unchecked.
6. Click **Create repository**.

## 4. Upload the project

1. In the new empty repository, click **uploading an existing file**.
2. Drag the listed files and the `.github` folder into the upload area.
3. If GitHub does not accept the `.github` folder by drag-and-drop, click **Add file**, choose **Create new file**, type `.github/workflows/build-apk.yml` as the filename, and paste the contents of the local workflow file into it.
4. Scroll down and click **Commit changes**.

If you already uploaded the project, upload the changed `.github/workflows/build-apk.yml` again and commit it. GitHub only uses the workflow version that is committed in the repository.

For this build fix, make sure the workflow file in GitHub contains **Set up supported Python** with `python-version: '3.11'`, the pip pin `pip==24.3.1`, and **Remove stale Android build output**. Do not rerun an older workflow run; start a new run after committing.

After committing, the repository should show `.github`, `main.py`, `buildozer.spec`, `README.md`, `requirements.txt`, and `.gitignore`.

## 5. Start the APK build

1. Click the **Actions** tab.
2. Click **Build Android APK** on the left.
3. Click **Run workflow**.
4. Click the green **Run workflow** button.
5. Wait for the job to finish. The first build may take several minutes.
6. Click the completed workflow run.
7. Scroll to **Artifacts**.
8. Download `night-intervalometer-debug-apk`.

## 6. Install it on the Samsung phone

1. Unzip the downloaded artifact on the PC.
2. Send the APK to the Galaxy S21 FE, for example with USB, OneDrive, or email.
3. Open the APK on the phone.
4. If Android asks, allow the file manager or browser to install unknown apps.
5. Install and open the app.

This first APK tests the interface, movable controls, timing, total duration, and animations. Automatic tapping of Samsung Camera is not implemented yet; that requires a native Android accessibility or overlay service.
