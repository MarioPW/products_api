from fastapi.responses import JSONResponse
from fastapi import HTTPException
import smtplib
from email.message import EmailMessage
import ssl
from dotenv import load_dotenv
from os import getenv
from pydantic import EmailStr
import uuid
from .create_verification_code import create_verification_code

load_dotenv()

class EmailHandler:
    def __init__(self, email: EmailStr) -> None:
        self.email = email
        self.email_address = getenv("EMAIL")
        self.email_password = getenv("EMAIL_PASSWORD")
        self.change_password_endpiont = getenv("RESET_PASSWORD_ENDPIONT")
        self.verification_code = create_verification_code()
        self.reset_password_code = str(uuid.uuid1())

    def get_verification_code(self):
        return self.verification_code
    
    def get_reset_password_code(self):
        return self.reset_password_code
  
    def send_verification_email(self):
        msg = EmailMessage()
        msg['Subject'] = "Código de verificación www.dalanakids.com"
        msg['From'] = self.email_address
        msg['To'] = self.email
        html_message = f"""
        <html>
            <body>
              <div style="text-align: center;">
                <p style= "font-weight: bold;
                          font-family: sans-serif;"
                          >Ingresa este código para completar tu registro:</p>
                <p style="display: inline-block;
                          background-color: rgb(61, 61, 254);
                          padding: 7px 11px;
                          color: white;
                          border-radius: 11px;
                          font-size: 24px;
                          font-family: sans-serif;
                          letter-spacing: 3px;
                          ">{self.verification_code}
                </p>
              </div>
            </body>
          </html>
        """
        msg.set_content(html_message, subtype='html')
        context1 = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context1) as smtp:
                smtp.login(self.email_address, self.email_password)
                smtp.send_message(msg)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error sending email in email_handler.py: {e}")
      
    def send_change_password_email(self):
        msg = EmailMessage()
        msg['Subject'] = "Cambio de contraseña www.dalanakids.com"
        msg['From'] = self.email_address
        msg['To'] = self.email
        html_message = f"""
        <html>
            <body>
            <div>
              <h1 style= "font-weight: bold;
                        font-family: sans-serif;"
                        >Cambio de contraseña www.dalanakids.com</h1>
              <p>Presiona el botón a continuación para renovar tu contraseña. Recuerda no compartir este enlace con nadie.</p>
              <a type='submit' style="display:inline-block;
                        font-family:'RoobertPRO',Helvetica,Arial,sans-serif;
                        font-size:16px;line-height:24px;
                        color:#ffffff;background-color:#4262ff;
                        text-decoration:none;
                        padding:11px 16px 13px 16px;
                        border-radius:8px;
                        text-align:center;" 
                        href={self.change_password_endpiont + '/' + self.reset_password_code}>Reset Password</a>
              <p>Si no has solicitado renovar tu contraseña ignora este mensaje.<br>Tu contraseña no será cambiada.
                Felicidades! www.appdeproductos.com
              </p>
            </div>
            </body>
          </html>
        """
        msg.set_content(html_message, subtype='html')
        context1 = ssl.create_default_context()
        try:
          with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context1) as smtp:
              smtp.login(self.email_address, self.email_password)
              smtp.send_message(msg)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error sending change password email in email_handler.py: {e}")
  
# Test
if __name__ == "__main__":
    web_master_email = getenv('WEB_MASTER_EMAIL')
    mail = EmailHandler(web_master_email)
    mail.send_verification_email()