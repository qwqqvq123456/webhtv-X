package com.fongmi.android.tv.utils;

import org.junit.Test;

import java.net.URI;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class GithubTest {

    @Test
    public void updateChannelAssetsPointAtTheForkRepository() {
        String stable = Github.getChannelAsset("mobile-arm64_v8a.json");
        String beta = Github.getChannelAsset("mobile-arm64_v8a-beta.json");

        assertEquals("github.com", URI.create(stable).getHost());
        assertEquals(URI.create(stable).getHost(), URI.create(beta).getHost());
        assertTrue(stable.contains("/releases/download/update-channel/"));
        assertTrue(beta.contains("/releases/download/update-channel/"));
        assertEquals("https://github.com/qwqqvq123456/webhtv/releases/download/update-channel/mobile-arm64_v8a.json", stable);
        assertEquals("https://github.com/qwqqvq123456/webhtv/releases/download/update-channel/mobile-arm64_v8a-beta.json", beta);
    }

    @Test
    public void upstreamMirrorIsDisabledSoTheForkNeverInstallsTheOfficialBuild() {
        assertEquals("", Github.getCnbMirrorAsset("mobile-arm64_v8a-beta.json"));
        assertEquals("", Github.getCnbMirrorAsset("mobile-arm64_v8a.json"));
    }

    @Test
    public void releaseAssetUrlsStayOnTheFork() {
        String apk = Github.getGithubReleaseAsset("v5.6.0-beta-202611260200", "mobile-arm64_v8a-beta.apk");
        assertEquals("https://github.com/qwqqvq123456/webhtv/releases/download/v5.6.0-beta-202611260200/mobile-arm64_v8a-beta.apk", apk);
        assertEquals("https://api.github.com/repos/qwqqvq123456/webhtv/releases/latest", Github.getLatestReleaseApi());
    }
}
