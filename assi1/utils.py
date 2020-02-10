import threading

def create_thread(obj):
    obj_thread = threading.Thread(target=obj.run, daemon=True)
    obj_thread.start()
    while obj_thread.isAlive():
        obj_thread.join(1)
    obj_response = obj.get_response()
    return obj_response
