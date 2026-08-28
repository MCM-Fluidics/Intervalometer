package org.intervalometer;

import android.accessibilityservice.GestureDescription;
import android.accessibilityservice.AccessibilityService;
import android.app.Service;
import android.content.Intent;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.provider.Settings;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

public class OverlayService extends Service {
    private static OverlayService instance;
    private WindowManager windowManager;
    private WindowManager.LayoutParams rootParams;
    private FrameLayout root;
    private CrosshairView crosshair;
    private LinearLayout panel;
    private TextView status;
    private Handler handler = new Handler();
    private boolean running;
    private int shot;
    private int total;
    private float delay = 3f;
    private float pressLength = 1f;
    private float interval = 2f;

    public static void start(android.content.Context context) {
        Intent intent = new Intent(context, OverlayService.class);
        if (Build.VERSION.SDK_INT >= 26) context.startForegroundService(intent);
        else context.startService(intent);
    }

    @Override public void onCreate() {
        super.onCreate();
        instance = this;
        buildOverlay();
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (Build.VERSION.SDK_INT >= 26) {
            android.app.NotificationChannel channel = new android.app.NotificationChannel("intervalometer", "Intervalometer", android.app.NotificationManager.IMPORTANCE_LOW);
            getSystemService(android.app.NotificationManager.class).createNotificationChannel(channel);
            android.app.Notification notification = new android.app.Notification.Builder(this, "intervalometer")
                    .setContentTitle("Night Intervalometer").setContentText("Overlay is active").setSmallIcon(android.R.drawable.ic_menu_camera).build();
            startForeground(7, notification);
        }
        return START_STICKY;
    }

    private WindowManager.LayoutParams params(int type) {
        int windowType = Build.VERSION.SDK_INT >= 26 ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY : WindowManager.LayoutParams.TYPE_PHONE;
        return new WindowManager.LayoutParams(-2, -2, windowType, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, -3);
    }

    private void buildOverlay() {
        if (Build.VERSION.SDK_INT >= 23 && !Settings.canDrawOverlays(this)) return;
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.TRANSPARENT);

        crosshair = new CrosshairView();
        FrameLayout.LayoutParams crossParams = new FrameLayout.LayoutParams(116, 116);
        crossParams.gravity = Gravity.CENTER;
        root.addView(crosshair, crossParams);

        panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(18, 14, 18, 14);
        GradientDrawable panelBackground = new GradientDrawable();
        panelBackground.setColor(0xB8121822);
        panelBackground.setCornerRadius(18);
        panel.setBackground(panelBackground);
        addText("PLACE CROSS ON SHUTTER", 11, 0xFFD0D8E2);
        addField("DELAY", "3", 0);
        addField("LONG", "1", 1);
        addField("INTERVAL", "2", 2);
        addField("NUMBER", "5", 3);
        LinearLayout actions = new LinearLayout(this);
        actions.setOrientation(LinearLayout.VERTICAL);
        Button start = new Button(this); start.setText("START"); start.setOnClickListener(v -> startSequence());
        Button stop = new Button(this); stop.setText("STOP"); stop.setOnClickListener(v -> stopSequence());
        actions.addView(start, new LinearLayout.LayoutParams(150, 46));
        actions.addView(stop, new LinearLayout.LayoutParams(150, 46));
        panel.addView(actions);
        status = new TextView(this); status.setTextColor(0xFFFF7777); status.setText("READY"); status.setTextSize(11); panel.addView(status);
        rootParams = params(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY);
        rootParams.gravity = Gravity.TOP | Gravity.START; rootParams.x = 0; rootParams.y = 0;
        WindowManager.LayoutParams panelParams = params(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY);
        panelParams.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL;
        panelParams.gravity = Gravity.TOP | Gravity.START; panelParams.x = 24; panelParams.y = 96;
        windowManager.addView(root, rootParams);
        windowManager.addView(panel, panelParams);
        panel.setOnTouchListener(new DragListener(panelParams));
    }

    private void addText(String text, int size, int color) {
        TextView view = new TextView(this); view.setText(text); view.setTextSize(size); view.setTextColor(color); panel.addView(view, new LinearLayout.LayoutParams(-1, 32));
    }

    private void addField(String label, String value, int index) {
        LinearLayout row = new LinearLayout(this); row.setGravity(Gravity.CENTER_VERTICAL);
        TextView name = new TextView(this); name.setText(label); name.setTextColor(0xFFB8C2CE); name.setTextSize(10); row.addView(name, new LinearLayout.LayoutParams(82, 38));
        EditText edit = new EditText(this); edit.setText(value); edit.setTextColor(Color.WHITE); edit.setTextSize(13); edit.setSingleLine(true); edit.setTag(index); row.addView(edit, new LinearLayout.LayoutParams(70, 38));
        panel.addView(row);
    }

    private void startSequence() {
        if (running) return;
        running = true; shot = 0; readFields(); status.setText("WAITING / DELAY");
        handler.postDelayed(this::press, (long)(delay * 1000));
    }

    private void press() {
        if (!running) return;
        shot++; status.setText("PRESSING " + shot + " / " + total); crosshair.holding = true; crosshair.invalidate();
        AccessibilityTapService.hold(crosshair.getCenterXOnScreen(), crosshair.getCenterYOnScreen(), pressLength);
        handler.postDelayed(this::release, (long)(pressLength * 1000));
    }

    private void release() {
        crosshair.holding = false; crosshair.invalidate();
        if (!running) return;
        if (shot >= total) { running = false; status.setText("COMPLETE"); return; }
        status.setText("WAITING / INTERVAL"); handler.postDelayed(this::press, (long)(interval * 1000));
    }

    private void readFields() {
        for (int i = 0; i < panel.getChildCount(); i++) {
            View child = panel.getChildAt(i);
            if (!(child instanceof LinearLayout)) continue;
            LinearLayout row = (LinearLayout) child;
            for (int j = 0; j < row.getChildCount(); j++) {
                View item = row.getChildAt(j);
                if (!(item instanceof EditText)) continue;
                EditText edit = (EditText)item; float value;
                try { value = Float.parseFloat(edit.getText().toString()); } catch (Exception e) { value = ((Integer)edit.getTag() == 0) ? 3 : ((Integer)edit.getTag() == 1 ? 1 : ((Integer)edit.getTag() == 2 ? 2 : 5)); }
                int index = (Integer)edit.getTag(); if (index == 0) delay = Math.max(0, value); else if (index == 1) pressLength = Math.max(.1f, value); else if (index == 2) interval = Math.max(.1f, value); else total = Math.max(1, (int)value);
            }
        }
    }

    private void stopSequence() { running = false; handler.removeCallbacksAndMessages(null); crosshair.holding = false; crosshair.invalidate(); status.setText("STOPPED"); }

    @Override public void onDestroy() { stopSequence(); if (windowManager != null && root != null) windowManager.removeView(root); if (windowManager != null && panel != null) windowManager.removeView(panel); instance = null; super.onDestroy(); }
    @Override public IBinder onBind(Intent intent) { return null; }

    private class DragListener implements View.OnTouchListener {
        final WindowManager.LayoutParams p; float downX, downY; int startX, startY;
        DragListener(WindowManager.LayoutParams p) { this.p = p; }
        public boolean onTouch(View v, MotionEvent e) { if (e.getAction() == 0) { downX=e.getRawX(); downY=e.getRawY(); startX=p.x; startY=p.y; return true; } if (e.getAction() == 2) { p.x=startX+(int)(e.getRawX()-downX); p.y=startY+(int)(e.getRawY()-downY); windowManager.updateViewLayout(panel,p); return true; } return true; }
    }

    private class CrosshairView extends View {
        Paint paint = new Paint(1); boolean holding;
        CrosshairView() { super(OverlayService.this); setLayerType(View.LAYER_TYPE_SOFTWARE, null); }
        protected void onDraw(Canvas c) { super.onDraw(c); float x=getWidth()/2f,y=getHeight()/2f; paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(3); paint.setColor(holding ? 0xFFFF6666 : 0xFFF0222C); c.drawCircle(x,y,30,paint); c.drawLine(0,y,getWidth(),y,paint); c.drawLine(x,0,x,getHeight(),paint); if (holding) { paint.setColor(0x88FF3333); paint.setStrokeWidth(6); c.drawCircle(x,y,42,paint); } }
        float getCenterXOnScreen() { return getLocationOnScreen()[0] + getWidth()/2f; }
        float getCenterYOnScreen() { return getLocationOnScreen()[1] + getHeight()/2f; }
        public boolean onTouchEvent(MotionEvent e) { if (e.getAction()==0 || e.getAction()==2) { int[] location=getLocationOnScreen(); rootParams.x+=(int)e.getRawX()-location[0]-getWidth()/2; rootParams.y+=(int)e.getRawY()-location[1]-getHeight()/2; windowManager.updateViewLayout(root,rootParams); return true; } return true; }
    }
}
