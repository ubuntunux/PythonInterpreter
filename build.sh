export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export ANDROID_HOME=/home/ubuntunux/.buildozer/android/platform/android-sdk
unset ANDROID_SDK_HOME
adb logcat -c
buildozer android debug deploy run logcat | grep python