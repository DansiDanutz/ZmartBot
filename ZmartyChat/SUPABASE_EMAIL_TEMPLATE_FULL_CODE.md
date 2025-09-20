# 📧 SUPABASE EMAIL TEMPLATE - FULL CODE

## 🎯 WHERE TO PASTE THIS:
1. Go to: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/auth/templates
2. Click on "Confirm signup" template
3. Copy ALL the code below
4. Paste in the "Message" field
5. Set Subject to: `Welcome to ZmartyChat! 🎉 Verify Your Account`
6. Click Save

## 📋 FULL EMAIL TEMPLATE CODE:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your ZmartyChat Account</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f7fa;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f7fa; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 20px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08); overflow: hidden;">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #0066ff 0%, #4d94ff 100%); padding: 40px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 36px; font-weight: 700;">✨ ZmartyChat</h1>
                            <p style="margin: 10px 0 0 0; color: #e6f0ff; font-size: 18px;">Your AI-Powered Crypto Intelligence Platform</p>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px 0; color: #1a1a1a; font-size: 28px; font-weight: 600;">Welcome to ZmartyChat! 🎉</h2>

                            <p style="margin: 0 0 25px 0; color: #4a5568; font-size: 16px; line-height: 1.6;">
                                Thank you for joining the future of crypto intelligence. You're just one step away from accessing our powerful AI-driven platform that combines market analysis with intelligent conversation.
                            </p>

                            <!-- Verification Code Box -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 35px 0;">
                                <tr>
                                    <td align="center">
                                        <table cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f0f7ff 0%, #e8f2ff 100%); border: 3px solid #0066ff; border-radius: 20px; padding: 35px 45px; box-shadow: 0 5px 20px rgba(0, 102, 255, 0.15);">
                                            <tr>
                                                <td align="center">
                                                    <p style="margin: 0 0 12px 0; color: #4a5568; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600;">YOUR VERIFICATION CODE</p>
                                                    <p style="margin: 0; color: #0066ff; font-size: 48px; font-weight: 800; letter-spacing: 10px; font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Courier New', monospace; text-shadow: 2px 2px 4px rgba(0, 102, 255, 0.1);">{{ .Token }}</p>
                                                    <p style="margin: 12px 0 0 0; color: #718096; font-size: 13px;">⏱️ Valid for 60 minutes</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <!-- Features -->
                            <h3 style="margin: 35px 0 20px 0; color: #1a1a1a; font-size: 20px; font-weight: 600;">🚀 What You're Getting Access To:</h3>

                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 30px 0;">
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <table cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="width: 40px; vertical-align: top; font-size: 24px;">🧠</td>
                                                <td style="color: #4a5568; font-size: 15px; line-height: 1.6;">
                                                    <strong style="color: #1a1a1a; font-size: 16px;">ZmartyBrain Intelligence</strong><br>
                                                    Advanced AI that understands crypto markets and provides intelligent insights tailored to your needs
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <table cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="width: 40px; vertical-align: top; font-size: 24px;">🤖</td>
                                                <td style="color: #4a5568; font-size: 15px; line-height: 1.6;">
                                                    <strong style="color: #1a1a1a; font-size: 16px;">ZmartBot Trading Analysis</strong><br>
                                                    Real-time market data from 200+ cryptocurrencies across 100+ exchanges with predictive analytics
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <table cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="width: 40px; vertical-align: top; font-size: 24px;">💬</td>
                                                <td style="color: #4a5568; font-size: 15px; line-height: 1.6;">
                                                    <strong style="color: #1a1a1a; font-size: 16px;">Conversational AI Assistant</strong><br>
                                                    Chat naturally about markets, get explanations, and receive personalized insights
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <table cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="width: 40px; vertical-align: top; font-size: 24px;">📊</td>
                                                <td style="color: #4a5568; font-size: 15px; line-height: 1.6;">
                                                    <strong style="color: #1a1a1a; font-size: 16px;">Advanced Analytics Dashboard</strong><br>
                                                    Professional-grade charts, risk metrics, and portfolio analysis tools
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <table cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="width: 40px; vertical-align: top; font-size: 24px;">🔔</td>
                                                <td style="color: #4a5568; font-size: 15px; line-height: 1.6;">
                                                    <strong style="color: #1a1a1a; font-size: 16px;">Smart Alerts & Notifications</strong><br>
                                                    AI-powered alerts for market opportunities and important movements
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <!-- Pro Tip -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f0fff4 0%, #e6ffed 100%); border: 2px solid #10b981; border-radius: 12px; padding: 18px; margin: 25px 0;">
                                <tr>
                                    <td>
                                        <p style="margin: 0; color: #065f46; font-size: 14px; line-height: 1.6;">
                                            <strong>💡 Pro Tip:</strong> After verification, take our quick onboarding tour to unlock the full power of ZmartyChat. It only takes 2 minutes and will show you all the amazing features!
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Disclaimer -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f0f4ff; border-radius: 12px; padding: 15px; margin: 25px 0;">
                                <tr>
                                    <td>
                                        <p style="margin: 0; color: #2d3748; font-size: 13px; line-height: 1.5;">
                                            <strong>📌 Important:</strong> ZmartyChat provides market data, analysis tools, and AI insights for informational purposes only. We do not offer financial advice or investment recommendations. All trading decisions are your own responsibility. Always do your own research.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Security Note -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fef5e7; border-radius: 12px; padding: 15px; margin: 25px 0;">
                                <tr>
                                    <td>
                                        <p style="margin: 0; color: #7a6a00; font-size: 14px; line-height: 1.5;">
                                            <strong>🔒 Security Note:</strong> If you didn't create a ZmartyChat account, please ignore this email. Your email address will not be used without verification. This code expires in 60 minutes for your security.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- How to use -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fafafa; border-radius: 12px; padding: 20px; margin: 30px 0;">
                                <tr>
                                    <td>
                                        <h4 style="margin: 0 0 12px 0; color: #1a1a1a; font-size: 16px;">How to verify your account:</h4>
                                        <ol style="margin: 0; padding-left: 20px; color: #4a5568; font-size: 14px; line-height: 1.8;">
                                            <li>Go back to the ZmartyChat registration page</li>
                                            <li>Enter the 6-digit code shown above</li>
                                            <li>Click "Verify" to complete your registration</li>
                                            <li>Start exploring your new AI-powered crypto companion!</li>
                                        </ol>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 35px; text-align: center; border-top: 2px solid #e2e8f0;">
                            <h3 style="margin: 0 0 10px 0; color: #0066ff; font-size: 18px; font-weight: 700;">Welcome to the ZmartyChat Community! 🎊</h3>
                            <p style="margin: 0 0 20px 0; color: #718096; font-size: 15px;">Where AI meets Crypto Intelligence</p>

                            <table cellpadding="0" cellspacing="0" align="center" style="margin: 20px 0;">
                                <tr>
                                    <td style="padding: 0 12px;">
                                        <a href="https://zmartychat.app" style="color: #0066ff; text-decoration: none; font-size: 14px; font-weight: 600;">🌐 Website</a>
                                    </td>
                                    <td style="color: #cbd5e0; font-size: 14px;">•</td>
                                    <td style="padding: 0 12px;">
                                        <a href="https://zmartychat.app/docs" style="color: #0066ff; text-decoration: none; font-size: 14px; font-weight: 600;">📚 Documentation</a>
                                    </td>
                                    <td style="color: #cbd5e0; font-size: 14px;">•</td>
                                    <td style="padding: 0 12px;">
                                        <a href="https://zmartychat.app/support" style="color: #0066ff; text-decoration: none; font-size: 14px; font-weight: 600;">💬 Support</a>
                                    </td>
                                </tr>
                            </table>

                            <table cellpadding="0" cellspacing="0" align="center" style="margin: 20px 0;">
                                <tr>
                                    <td style="padding: 0 8px;">
                                        <a href="https://twitter.com/zmartychat" style="color: #4a5568; text-decoration: none; font-size: 20px;">𝕏</a>
                                    </td>
                                    <td style="padding: 0 8px;">
                                        <a href="https://discord.gg/zmartychat" style="color: #4a5568; text-decoration: none; font-size: 20px;">💬</a>
                                    </td>
                                    <td style="padding: 0 8px;">
                                        <a href="https://t.me/zmartychat" style="color: #4a5568; text-decoration: none; font-size: 20px;">✈️</a>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 25px 0 0 0; color: #a0aec0; font-size: 12px; line-height: 1.6;">
                                © 2025 ZmartyChat. All rights reserved.<br>
                                This email was sent to {{ .Email }} from ZmartyChat<br>
                                <a href="https://zmartychat.app/privacy" style="color: #a0aec0; text-decoration: underline;">Privacy Policy</a> •
                                <a href="https://zmartychat.app/terms" style="color: #a0aec0; text-decoration: underline;">Terms of Service</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
```

## ✅ IMPORTANT NOTES:

1. **Copy ALL the code** - From `<!DOCTYPE html>` to `</html>`
2. **Don't modify** the `{{ .Token }}` and `{{ .Email }}` - These are Supabase variables
3. **Disclaimer included** - No financial advice, informational only
4. **Professional design** - Gradients, cards, proper spacing
5. **Mobile responsive** - Works on all devices

## 🎯 After Pasting:
1. Save the template
2. Test by registering a new user
3. Check that the email looks professional
4. Verify the 6-digit code displays correctly