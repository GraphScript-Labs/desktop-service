from webview import Window, create_window, start

from api import API

if __name__ == '__main__':
  frontend_path = "http://localhost:3000"
  api: API = API()

  window: Window = create_window(
    title='GraphScript',
    url=frontend_path,
    js_api=api,
    width=1200,
    height=800,
    transparent=True,
    frameless=True,
    vibrancy=True,
    easy_drag=False,
  )
  
  api.attach_window(window)
  start(debug=True)

