# Proguard rules for minimal native WebView app
-keepattributes JavascriptInterface
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-dontwarn android.webkit.**
