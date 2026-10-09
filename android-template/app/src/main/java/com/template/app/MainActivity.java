package {{PACKAGE_NAME}};

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.Toast;

public class MainActivity extends Activity {

    private WebView webView;
    private ProgressBar progressBar;
    private ValueCallback<Uri[]> fileUploadCallback;
    private final static int FILE_CHOOSER_REQUEST_CODE = 1001;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);

        setupWebView();

        String targetUrl = getString(R.string.target_url);
        if (savedInstanceState != null) {
            webView.restoreState(savedInstanceState);
        } else {
            webView.loadUrl(targetUrl);
        }
    }

    private void setupWebView() {
        WebSettings settings = webView.getSettings();

        // Core WebView Settings (Simple - Fast - Lightweight)
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        // Support cookies and 3rd party cookies for login/session persistence
        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            cookieManager.setAcceptThirdPartyCookies(webView, true);
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW); // Enforce HTTPS
        }

        // Custom WebViewClient to stay inside WebView while opening special intents externally
        webView.setWebViewClient(new CustomWebViewClient());

        // Custom WebChromeClient for progress bar and file upload support
        webView.setWebChromeClient(new CustomWebChromeClient());
    }

    private class CustomWebViewClient extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, String url) {
            return handleUrl(view, Uri.parse(url));
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                return handleUrl(view, request.getUrl());
            }
            return false;
        }

        private boolean handleUrl(WebView view, Uri uri) {
            String scheme = uri.getScheme();
            String host = uri.getHost();

            if (scheme == null) {
                return false;
            }

            // Handle external apps: WhatsApp, Telegram, Phone, Email, SMS, Maps, Play Store
            boolean isExternalScheme = scheme.equalsIgnoreCase("whatsapp") ||
                                       scheme.equalsIgnoreCase("tg") ||
                                       scheme.equalsIgnoreCase("tel") ||
                                       scheme.equalsIgnoreCase("mailto") ||
                                       scheme.equalsIgnoreCase("sms") ||
                                       scheme.equalsIgnoreCase("geo") ||
                                       scheme.equalsIgnoreCase("market");

            boolean isExternalDomain = (host != null) && (
                host.equalsIgnoreCase("api.whatsapp.com") ||
                host.equalsIgnoreCase("wa.me") ||
                host.equalsIgnoreCase("t.me") ||
                host.equalsIgnoreCase("maps.google.com") ||
                host.equalsIgnoreCase("maps.app.goo.gl")
            );

            if (isExternalScheme || isExternalDomain) {
                try {
                    Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                    startActivity(intent);
                    return true;
                } catch (ActivityNotFoundException e) {
                    Toast.makeText(MainActivity.this, "No application found to handle this link", Toast.LENGTH_SHORT).show();
                    return true;
                }
            }

            // All standard web requests stay inside the WebView
            return false;
        }

        @Override
        public void onPageStarted(WebView view, String url, Bitmap favicon) {
            if (progressBar != null) {
                progressBar.setVisibility(View.VISIBLE);
            }
            super.onPageStarted(view, url, favicon);
        }

        @Override
        public void onPageFinished(WebView view, String url) {
            if (progressBar != null) {
                progressBar.setVisibility(View.GONE);
            }
            CookieManager.getInstance().flush();
            super.onPageFinished(view, url);
        }
    }

    private class CustomWebChromeClient extends WebChromeClient {
        @Override
        public void onProgressChanged(WebView view, int newProgress) {
            if (progressBar != null) {
                progressBar.setProgress(newProgress);
                if (newProgress >= 100) {
                    progressBar.setVisibility(View.GONE);
                } else {
                    progressBar.setVisibility(View.VISIBLE);
                }
            }
            super.onProgressChanged(view, newProgress);
        }

        // Support HTML file input / form uploads
        @Override
        public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {
            if (fileUploadCallback != null) {
                fileUploadCallback.onReceiveValue(null);
            }
            fileUploadCallback = filePathCallback;

            Intent intent = null;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                intent = fileChooserParams.createIntent();
            } else {
                intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("*/*");
            }

            try {
                startActivityForResult(intent, FILE_CHOOSER_REQUEST_CODE);
                return true;
            } catch (ActivityNotFoundException e) {
                fileUploadCallback = null;
                Toast.makeText(MainActivity.this, "Cannot open file picker", Toast.LENGTH_SHORT).show();
                return false;
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
            if (fileUploadCallback != null) {
                Uri[] results = null;
                if (resultCode == Activity.RESULT_OK && data != null) {
                    String dataString = data.getDataString();
                    if (dataString != null) {
                        results = new Uri[]{Uri.parse(dataString)};
                    }
                }
                fileUploadCallback.onReceiveValue(results);
                fileUploadCallback = null;
            }
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    // Android back button handling: goBack() in history, else finish()
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && event.getAction() == KeyEvent.ACTION_DOWN) {
            if (webView != null && webView.canGoBack()) {
                webView.goBack();
                return true;
            } else {
                finish();
                return true;
            }
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        if (webView != null) {
            webView.saveState(outState);
        }
    }
}
