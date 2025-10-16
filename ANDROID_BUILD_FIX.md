# Android APK Build Failure Fix

## Issue Identified
The Android APK build was failing with the error:
```
java.io.IOException: Tag number over 30 is not supported
```

This error occurs when the Android keystore used for signing the APK is incompatible with the Java version being used in the build process.

## Root Cause
The keystore stored in GitHub secrets (`ANDROID_KEYSTORE_BASE64`) was likely created with a different Java version or using an algorithm that's not compatible with Java 17, which was configured in the build.

## Solution Applied

### 1. Java Version Downgrade
Changed from Java 17 to Java 11 for better keystore compatibility:
- Updated `android/app/build.gradle` to use Java 11
- Updated `.github/workflows/build-android.yml` to use Java 11

### 2. Enhanced Signing Configuration
Added v1 and v2 signing support in `android/app/build.gradle` for better compatibility:
```gradle
v1SigningEnabled true
v2SigningEnabled true
```

### 3. Improved Error Handling
Added keystore validation and error handling in the GitHub workflow to provide better diagnostics if the issue persists.

## Next Steps for Complete Resolution

### Option 1: Regenerate the Keystore (Recommended)
Generate a new keystore using Java 11:

```bash
# On a system with Java 11 installed
keytool -genkey -v -keystore release.keystore \
  -alias ielts-release \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass [YourPassword] \
  -keypass [YourKeyPassword]
```

Then encode it to base64 and update the GitHub secret:
```bash
base64 release.keystore > keystore.txt
# Copy the contents of keystore.txt to ANDROID_KEYSTORE_BASE64 secret
```

### Option 2: Convert Existing Keystore
If you need to keep the existing keystore, convert it to a compatible format:

```bash
# Convert to PKCS12 format (more compatible)
keytool -importkeystore \
  -srckeystore old.keystore \
  -destkeystore new.keystore \
  -deststoretype pkcs12
```

## GitHub Secrets Required
Ensure these secrets are properly configured in your GitHub repository:
- `ANDROID_KEYSTORE_BASE64` - Base64 encoded keystore file
- `ANDROID_KEYSTORE_PASSWORD` - Keystore password
- `ANDROID_KEY_ALIAS` - Key alias name
- `ANDROID_KEY_PASSWORD` - Key password

## Testing the Fix
1. The next push to the repository will trigger the updated workflow
2. The build should now use Java 11 and handle the keystore properly
3. If issues persist, check the workflow logs for the keystore validation output

## Verification
After applying this fix, the Android build should complete successfully and produce:
- Debug APK for non-main branches
- Signed Release APK for main branch

## Files Modified
- `android/app/build.gradle` - Java version and signing configuration
- `.github/workflows/build-android.yml` - Java version and error handling