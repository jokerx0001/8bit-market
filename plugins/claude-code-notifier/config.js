module.exports = {
  feishu: {
    // Required for both sending notifications and receiving replies
    appId: 'cli_xxxxxxxxxx',           // Replace with your Feishu App ID
    appSecret: 'xxxxxxxxxxxxxxxx',       // Replace with your Feishu App Secret
    webhookUrl: 'https://open.feishu.cn/',  // Webhook URL for notifications

    // Optional: Custom notification channel
    chatId: '',  // Specific chat ID to send notifications to (empty = use webhook default)
  },

  notification: {
    // What events trigger notifications
    onAskUserQuestion: true,     // Claude asks user a question
    onPermissionRequest: true,   // Permission confirmations (delete, git push --force, etc.)
    onTaskComplete: false,       // Task completion (usually not needed)
    onTaskFail: true,            // Task failures
  },

  // Advanced
  pipePath: '/tmp/claude-code-notifier/pipe',  // Named pipe location
}
