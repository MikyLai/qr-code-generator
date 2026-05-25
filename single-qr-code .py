import qrcode
import io

url = "https://mixter-t.com/"
qr_img = qrcode.make(url)

qr_img.save("qr.png")