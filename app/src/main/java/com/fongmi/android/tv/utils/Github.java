package com.fongmi.android.tv.utils;

/**
 * Release and download endpoints for the update checker.
 *
 * <p>This fork publishes its own builds, so every update URL points at the fork repository.
 * Keeping the owner and repository name in one place means a future rename only touches the two
 * constants below instead of the whole update stack.
 *
 * <p>The upstream CNB mirror is disabled on purpose: the checker reads the fork manifest first and
 * falls back to the mirror only when that read fails. Leaving the upstream mirror in place would
 * let a transient network error offer the official package as an update, which would silently
 * replace the fork build (and its signature) with the upstream one.
 */
public class Github {

    /** Fork that publishes the update manifests and APKs. */
    public static final String REPO_OWNER = "qwqqvq123456";
    public static final String REPO_NAME = "webhtv";

    private static final String GITHUB_LATEST = "https://github.com/" + REPO_OWNER + "/" + REPO_NAME + "/releases/latest/download";
    private static final String GITHUB_RELEASE = "https://github.com/" + REPO_OWNER + "/" + REPO_NAME + "/releases/download";
    private static final String GITHUB_UPDATE_CHANNEL = GITHUB_RELEASE + "/update-channel";
    private static final String GITHUB_API = "https://api.github.com/repos/" + REPO_OWNER + "/" + REPO_NAME + "/releases/tags";
    private static final String GITHUB_RELEASES_API = "https://api.github.com/repos/" + REPO_OWNER + "/" + REPO_NAME + "/releases";
    private static final String GITHUB_RELEASE_ASSETS_API = "https://api.github.com/repos/" + REPO_OWNER + "/" + REPO_NAME + "/releases/assets";

    public static String getChannelAsset(String name) {
        return GITHUB_UPDATE_CHANNEL + "/" + name;
    }

    /**
     * Upstream mirror is not used by this fork; an empty value makes the checker skip it and move
     * on to the fork releases API instead of reading an official manifest.
     */
    public static String getCnbMirrorAsset(String name) {
        return "";
    }

    public static String getCnbAsset(String name) {
        return getGithubLatestAsset(name);
    }

    public static String getGithubLatestAsset(String name) {
        return GITHUB_LATEST + "/" + name;
    }

    public static String getGithubReleaseAsset(String tag, String name) {
        return GITHUB_RELEASE + "/" + tag + "/" + name;
    }

    public static String getJson(String name) {
        return getCnbAsset(name + ".json");
    }

    public static String getJson(String name, String channel) {
        if ("beta".equals(channel)) return getCnbAsset(name + "-beta.json");
        return getJson(name);
    }

    public static String getApk(String name) {
        return getCnbAsset(name + ".apk");
    }

    public static String getApk(String name, String channel) {
        if ("beta".equals(channel)) return getCnbAsset(name + "-beta.apk");
        return getApk(name);
    }

    public static String getAsset(String name, String channel) {
        return getCnbAsset(name);
    }

    public static String getReleaseApi(String tag) {
        return GITHUB_API + "/" + tag;
    }

    public static String getReleasesApi() {
        return GITHUB_RELEASES_API + "?per_page=20";
    }

    public static String getLatestReleaseApi() {
        return GITHUB_RELEASES_API + "/latest";
    }

    public static String getReleaseAssetApi(long id) {
        return GITHUB_RELEASE_ASSETS_API + "/" + id;
    }
}
