package {{PACKAGE_NAME}};

import android.annotation.TargetApi;
import android.app.Activity;
import android.app.DownloadManager;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.DownloadListener;
import android.webkit.URLUtil;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

public class MainActivity extends Activity {

    private WebView webView;
    private ProgressBar progressBar;
    private SwipeRefreshLayout swipeRefreshLayout;
    private View offlineLayout;
    private View splashLayout;
    private Button btnRetry;
    private boolean isSplashDismissed = false;

    private ValueCallback<Uri[]> fileUploadCallback;
    private final static int FILE_CHOOSER_REQUEST_CODE = 1001;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);
        offlineLayout = findViewById(R.id.offlineLayout);
        splashLayout = findViewById(R.id.splashLayout);
        btnRetry = findViewById(R.id.btnRetry);

        setupPullToRefresh();
        setupOfflineRetry();
        setupWebView();
        setupDownloadListener();

        // Safety timer: Dismiss splash after max 2.5s regardless of network speed
        new Handler(Looper.getMainLooper()).postDelayed(this::dismissSplash, 2500);

        String targetUrl = getString(R.string.target_url);
        if (savedInstanceState != null) {
            webView.restoreState(savedInstanceState);
        } else {
            if (isNetworkAvailable()) {
                webView.loadUrl(targetUrl);
            } else {
                showOfflineError();
                dismissSplash();
            }
        }
    }

    private void setupPullToRefresh() {
        if (swipeRefreshLayout != null) {
            swipeRefreshLayout.setColorSchemeColors(Color.parseColor("#2563EB"), Color.parseColor("#1D4ED8"));
            swipeRefreshLayout.setOnRefreshListener(() -> {
                if (isNetworkAvailable()) {
                    hideOfflineError();
                    webView.reload();
                } else {
                    swipeRefreshLayout.setRefreshing(false);
                    showOfflineError();
                }
            });
            // Ensure swipe refresh only triggers when scrolled to the very top
            swipeRefreshLayout.setOnChildScrollUpCallback((parent, child) -> webView != null && webView.getScrollY() > 0);
        }
    }

    private void setupOfflineRetry() {
        if (btnRetry != null) {
            btnRetry.setOnClickListener(v -> {
                if (isNetworkAvailable()) {
                    hideOfflineError();
                    String curUrl = webView.getUrl();
                    if (curUrl == null || curUrl.isEmpty() || curUrl.equals("about:blank")) {
                        webView.loadUrl(getString(R.string.target_url));
                    } else {
                        webView.reload();
                    }
                } else {
                    Toast.makeText(MainActivity.this, "Koneksi internet belum tersedia. Silakan periksa jaringan Anda.", Toast.LENGTH_SHORT).show();
                }
            });
        }
    }

    private void dismissSplash() {
        if (!isSplashDismissed && splashLayout != null) {
            isSplashDismissed = true;
            splashLayout.animate()
                    .alpha(0f)
                    .setDuration(300)
                    .withEndAction(() -> splashLayout.setVisibility(View.GONE));
        }
    }

    private void showOfflineError() {
        if (offlineLayout != null) {
            offlineLayout.setVisibility(View.VISIBLE);
        }
        if (swipeRefreshLayout != null) {
            swipeRefreshLayout.setRefreshing(false);
        }
        if (progressBar != null) {
            progressBar.setVisibility(View.GONE);
        }
    }

    private void hideOfflineError() {
        if (offlineLayout != null) {
            offlineLayout.setVisibility(View.GONE);
        }
    }

    private boolean isNetworkAvailable() {
        ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        if (cm == null) return false;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Network network = cm.getActiveNetwork();
            if (network == null) return false;
            NetworkCapabilities act = cm.getNetworkCapabilities(network);
            return act != null && (act.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
                    act.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ||
                    act.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET));
        } else {
            NetworkInfo netInfo = cm.getActiveNetworkInfo();
            return netInfo != null && netInfo.isConnected();
        }
    }

    private void setupDownloadListener() {
        if (webView != null) {
            webView.setDownloadListener(new DownloadListener() {
                @Override
                public void onDownloadStart(String url, String userAgent, String contentDisposition, String mimetype, long contentLength) {
                    try {
                        DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
                        if (mimetype != null && !mimetype.isEmpty()) {
                            request.setMimeType(mimetype);
                        }
                        String cookies = CookieManager.getInstance().getCookie(url);
                        if (cookies != null) {
                            request.addRequestHeader("cookie", cookies);
                        }
                        if (userAgent != null) {
                            request.addRequestHeader("User-Agent", userAgent);
                        }
                        String filename = URLUtil.guessFileName(url, contentDisposition, mimetype);
                        request.setDescription("Mengunduh berkas...");
                        request.setTitle(filename);
                        request.allowScanningByMediaScanner();
                        request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                        request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename);

                        DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                        if (dm != null) {
                            dm.enqueue(request);
                            Toast.makeText(MainActivity.this, "Memulai unduhan: " + filename, Toast.LENGTH_SHORT).show();
                        }
                    } catch (Exception e) {
                        try {
                            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                            startActivity(intent);
                        } catch (Exception ex) {
                            Toast.makeText(MainActivity.this, "Gagal mengunduh file", Toast.LENGTH_SHORT).show();
                        }
                    }
                }
            });
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
            if (swipeRefreshLayout != null) {
                swipeRefreshLayout.setRefreshing(false);
            }
            dismissSplash();
            CookieManager.getInstance().flush();
            super.onPageFinished(view, url);
        }

        @Override
        public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
            super.onReceivedError(view, errorCode, description, failingUrl);
            showOfflineError();
        }

        @TargetApi(Build.VERSION_CODES.M)
        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            super.onReceivedError(view, request, error);
            if (request.isForMainFrame()) {
                showOfflineError();
            }
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
            if (offlineLayout != null && offlineLayout.getVisibility() == View.VISIBLE) {
                finish();
                return true;
            }
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
        if (offlineLayout != null && offlineLayout.getVisibility() == View.VISIBLE) {
            super.onBackPressed();
        } else if (webView != null && webView.canGoBack()) {
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
