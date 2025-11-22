const { chromium } = require('playwright');

(async () => {
  // Configuration
  const MEETING_URL = 'https://us05web.zoom.us/j/82473846342?pwd=qfmnXt8iKS2lGzjbDyrcrzBAk41bUc.1';
  const BOT_NAME = 'SpoonBot';

  console.log('🚀 Launching SpoonBot...');

  // Launch browser
  // headless: false helps debug visually. Set to true for production/servers.
  const browser = await chromium.launch({ 
    headless: false, 
    args: [
      '--use-fake-ui-for-media-stream', // Auto-accept camera/mic permissions
      '--use-fake-device-for-media-stream' // Use fake media streams
    ]
  });
  const context = await browser.newContext({
    permissions: ['microphone', 'camera'],
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();

  // 1. Transform URL to Web Client URL to avoid "Open Zoom App" popups
  // Format: https://zoom.us/wc/{meetingId}/join?pwd={pwd}
  const urlObj = new URL(MEETING_URL);
  const meetingId = urlObj.pathname.split('/').pop(); // gets '82473846342'
  const pwd = urlObj.searchParams.get('pwd');
  
  // Construct Web Client URL
  const webClientUrl = `https://${urlObj.hostname}/wc/${meetingId}/join?pwd=${pwd}`; // &prefer=0 to force web client sometimes needed
  
  console.log(`🔗 Navigating to Web Client: ${webClientUrl}`);
  
  await page.goto(webClientUrl);

  // 2. Handle "Cookie Preferences" (OneTrust) if it appears
  try {
    const cookieBtn = await page.getByRole('button', { name: /Accept|Agree|Continue/i }).first();
    if (await cookieBtn.isVisible({ timeout: 5000 })) {
        console.log('🍪 Accepting cookies...');
        await cookieBtn.click();
    }
  } catch (e) {
    // Ignore if no cookie banner
  }

  // 3. Handle Name Input
  console.log('✍️ Entering name...');
  try {
    // Wait for the input field
    await page.waitForSelector('input[type="text"], #input-for-name', { timeout: 15000 });
    
    // Type name
    const nameInput = page.locator('input[type="text"], #input-for-name').first();
    await nameInput.fill(BOT_NAME);
    
    // 4. Click Join
    console.log('Hz Clicking Join...');
    const joinBtn = page.locator('button.preview-join-button'); // Common class for web client join
    
    // Fallback selector strategies
    if (await joinBtn.isVisible()) {
        await joinBtn.click();
    } else {
        await page.getByRole('button', { name: /Join/i }).click();
    }

  } catch (error) {
    console.log('⚠️  Might already be joined or different flow detected.');
  }

  // 5. Wait for connection
  console.log('⏳ Waiting to join meeting...');
  
  // Check for "Stay inside this tab" or "Join Audio" to confirm success
  try {
    await page.waitForSelector('.footer__leave-btn, button[aria-label="Leave"], .meeting-info-icon__icon-wrap', { timeout: 30000 });
    console.log('✅ Successfully joined the meeting!');
  } catch (e) {
    console.log('❌ Timed out waiting for meeting to fully load. Check screenshots.');
  }

  // Keep open for a while to simulate attendance
  console.log('🤖 SpoonBot is lurking... (Press Ctrl+C to stop)');
  
  // In a real bot, you would now attach listeners to audio streams or keep the process alive
  // await browser.close(); 
})();

