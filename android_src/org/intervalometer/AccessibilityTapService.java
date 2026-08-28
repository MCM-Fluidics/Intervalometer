package org.intervalometer;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.view.accessibility.AccessibilityEvent;

public class AccessibilityTapService extends AccessibilityService {
    private static AccessibilityTapService instance;

    @Override public void onServiceConnected() { instance = this; }
    @Override public void onAccessibilityEvent(AccessibilityEvent event) { }
    @Override public void onInterrupt() { instance = null; }

    public static void hold(float x, float y, float seconds) {
        if (instance == null) return;
        Path path = new Path(); path.moveTo(x, y);
        long duration = Math.max(100, (long)(seconds * 1000));
        GestureDescription.StrokeDescription stroke = new GestureDescription.StrokeDescription(path, 0, duration);
        instance.dispatchGesture(new GestureDescription.Builder().addStroke(stroke).build(), null, null);
    }
}
