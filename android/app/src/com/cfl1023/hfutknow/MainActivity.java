package com.cfl1023.hfutknow;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;

/**
 * 工大知道 —— 校园信息聚合站的外壳。
 * 内容全部来自 https://cfl1023.github.io/hfutknow/（GitHub Pages，
 * 云端每 5 分钟自动更新），本应用只是一个无广告的浏览器壳：
 * 提供沉浸式全屏、加载进度、断网重试、返回键回退。
 */
public class MainActivity extends Activity {

    private static final String HOME_URL = "https://cfl1023.github.io/hfutknow/";

    private WebView webView;
    private ProgressBar progressBar;
    private View errorView;
    private TextView errorText;
    private Button retryButton;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        progressBar = findViewById(R.id.progress);
        errorView = findViewById(R.id.error_view);
        errorText = findViewById(R.id.error_text);
        retryButton = findViewById(R.id.btn_retry);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);      // 站点用 localStorage 记忆主题/语言/排序
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(false);
        settings.setTextZoom(100);

        // 不注入任何第三方脚本；让站点自己的 Service Worker 管离线缓存
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                if (isExternal(url)) {
                    openExternally(url);
                    return true;
                }
                return false; // 站内链接留在壳里
            }

            @SuppressWarnings("deprecation")
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (isExternal(url)) {
                    openExternally(url);
                    return true;
                }
                return false;
            }

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                progressBar.setVisibility(View.VISIBLE);
                errorView.setVisibility(View.GONE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                progressBar.setVisibility(View.GONE);
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                // 只在整页加载失败时显示重试；子资源失败忽略
                if (failingUrl == null || failingUrl.equals(view.getUrl()) || view.getUrl() == null) {
                    showError();
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setProgress(newProgress);
                if (newProgress >= 100) {
                    progressBar.setVisibility(View.GONE);
                }
            }
        });

        retryButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                loadHome();
            }
        });
        loadHome();
    }

    private boolean isExternal(String url) {
        if (url == null || url.isEmpty()) {
            return false;
        }
        String host = Uri.parse(url).getHost();
        if (host == null) {
            return false;
        }
        return !host.equals("cfl1023.github.io");
    }

    private void openExternally(String url) {
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Exception ignored) {
            // 没有可处理的浏览器时静默失败，不影响壳内浏览
        }
    }

    private void loadHome() {
        errorView.setVisibility(View.GONE);
        progressBar.setVisibility(View.VISIBLE);
        webView.loadUrl(HOME_URL);
    }

    private void showError() {
        progressBar.setVisibility(View.GONE);
        errorText.setText(R.string.error_network);
        errorView.setVisibility(View.VISIBLE);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
