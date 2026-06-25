from core.models import EmailConfig
from django.core.mail import EmailMessage, get_connection


def EmailOTPSend(otp_object):
    email_config = EmailConfig.objects.filter(is_active=True).first()
    if not email_config:
        raise Exception("No active email configuration found.")
    
    email = otp_object.user.email
    otp = otp_object.otp_code
    
    subject = "Your OTP Code for Right Routes"
    html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>RatedDocs Verification Code</title>
        </head>
        <body style="margin:0;padding:0;background:#f3f7fb;font-family:Arial,Helvetica,sans-serif;">

            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f7fb;padding:30px 0;">
                <tr>
                    <td align="center">

                        <table width="650" cellpadding="0" cellspacing="0"
                            style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.08);">

                            <!-- Header -->
                            <tr>
                                <td align="center"
                                    style="background:linear-gradient(135deg,#0f766e,#14b8a6);padding:40px 30px;">

                                    <div style="
                                        width:70px;
                                        height:70px;
                                        line-height:70px;
                                        background:rgba(255,255,255,0.15);
                                        border-radius:50%;
                                        font-size:34px;
                                        margin:auto;
                                        color:#ffffff;
                                    ">
                                        🦷
                                    </div>

                                    <h1 style="
                                        color:#ffffff;
                                        margin:20px 0 10px;
                                        font-size:32px;
                                        font-weight:700;
                                    ">
                                        RatedDocs
                                    </h1>

                                    <p style="
                                        margin:0;
                                        color:#d1fae5;
                                        font-size:16px;
                                    ">
                                        Dentist & Patient Online Treatment Platform
                                    </p>

                                </td>
                            </tr>

                            <!-- Content -->
                            <tr>
                                <td style="padding:45px 40px;">

                                    <h2 style="
                                        margin-top:0;
                                        color:#0f172a;
                                        font-size:26px;
                                    ">
                                        Verify Your Account
                                    </h2>

                                    <p style="
                                        color:#475569;
                                        font-size:16px;
                                        line-height:1.8;
                                    ">
                                        Hello,
                                    </p>

                                    <p style="
                                        color:#475569;
                                        font-size:16px;
                                        line-height:1.8;
                                    ">
                                        We received a request to verify your account on
                                        <strong>RatedDocs</strong>.
                                        Please use the verification code below to continue.
                                    </p>

                                    <!-- OTP Card -->
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center">

                                                <div style="
                                                    background:linear-gradient(135deg,#0f766e,#14b8a6);
                                                    border-radius:18px;
                                                    padding:30px;
                                                    margin:25px 0;
                                                    box-shadow:0 8px 25px rgba(20,184,166,0.25);
                                                ">
                                                    <div style="
                                                        color:#ffffff;
                                                        font-size:46px;
                                                        font-weight:bold;
                                                        letter-spacing:12px;
                                                        font-family:'Courier New', monospace;
                                                    ">
                                                        {otp}
                                                    </div>
                                                </div>

                                            </td>
                                        </tr>
                                    </table>

                                    <p style="
                                        text-align:center;
                                        font-size:18px;
                                        font-weight:600;
                                        color:#0f766e;
                                    ">
                                        This code will expire in 15 minutes.
                                    </p>

                                    <!-- Security Box -->
                                    <div style="
                                        background:#fefce8;
                                        border-left:5px solid #eab308;
                                        border-radius:10px;
                                        padding:18px;
                                        margin-top:35px;
                                    ">
                                        <strong style="
                                            color:#854d0e;
                                            font-size:16px;
                                        ">
                                            Security Reminder
                                        </strong>

                                        <p style="
                                            margin:10px 0 0;
                                            color:#713f12;
                                            line-height:1.7;
                                        ">
                                            Never share this verification code with anyone.
                                            RatedDocs staff and dentists will never ask
                                            for your OTP.
                                        </p>
                                    </div>

                                    <p style="
                                        margin-top:30px;
                                        color:#64748b;
                                        line-height:1.8;
                                    ">
                                        If you did not request this verification code,
                                        please ignore this email. No further action is required.
                                    </p>

                                    <p style="
                                        margin-top:35px;
                                        color:#475569;
                                    ">
                                        Regards,<br>
                                        <strong>RatedDocs Team</strong>
                                    </p>

                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td align="center"
                                    style="
                                        background:#f8fafc;
                                        border-top:1px solid #e2e8f0;
                                        padding:30px;
                                    ">

                                    <h3 style="
                                        margin:0;
                                        color:#0f172a;
                                    ">
                                        RatedDocs
                                    </h3>

                                    <p style="
                                        margin:10px 0;
                                        color:#64748b;
                                        font-size:14px;
                                    ">
                                        Connecting Patients with Trusted Dental Professionals
                                    </p>

                                    <p style="
                                        color:#94a3b8;
                                        font-size:13px;
                                        margin:15px 0 0;
                                    ">
                                        © 2026 RatedDocs. All Rights Reserved.
                                    </p>

                                    <p style="
                                        color:#94a3b8;
                                        font-size:12px;
                                        margin-top:10px;
                                    ">
                                        This is an automated email. Please do not reply.
                                    </p>

                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>
    """
    
    connection = get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=email_config.host,
        port=int(email_config.port),
        username=email_config.host_user,
        password=email_config.host_password,
        use_tls=email_config.tls,
        fail_silently=False,
    )
    email_message = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=f"{email_config.name} <{email_config.email}>",
        to=[email],
        connection=connection,
    )
    email_message.content_subtype = "html"

    try:
        email_message.send()
        print(
            f"[OTP] Successfully sent OTP "
            f"{otp} to {email}"
        )
        return True
    except Exception as e:
        print(
            f"[OTP] Failed to send OTP "
            f"to {email}: {str(e)}"
        )
        raise Exception(
            f"Failed to send OTP: {str(e)}"
        )




