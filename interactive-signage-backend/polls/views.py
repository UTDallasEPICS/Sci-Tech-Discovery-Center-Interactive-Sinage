#change id_received_once to false when the reset endpoint is called
#add receive_bin_id to urls.py

from django.shortcuts import render
from django.http import JsonResponse
from .getpath import getpath
#from .validID import validID


ID_RECEIVED_ONCE = False
CURRENT_BIN_ID = None # Placeholder for the current binary ID


def showinfo(request):
    #HTTP endpoint: /polls/?id=<id>&lang=<lang>

    #Reads `id` and optional `lang` from query params and calls getpath().
    #Returns 400 if id is missing, 404 if getpath returns an error for an invalid id,
    #otherwise 200 with the JSON payload.
    binary_id = None
    binary_id = request.GET.get("id")
    if binary_id is None:
        #id parameter missing
        return JsonResponse({"error": "Missing 'id' parameter"}, status=400)

    lang = request.GET.get("lang", "en")
    data = getpath(binary_id, lang)
    status = 404 if "error" in data else 200
    return JsonResponse(data, status=status)


# getRelativepath   

def receive_den_id(request):

    global ID_RECEIVED_ONCE, CURRENT_BIN_ID

    binary_id = request.GET.get("id")

    if ID_RECEIVED_ONCE :
        return JsonResponse({"message": f"ID {CURRENT_BIN_ID} already received. No more requests till reset"}, status=200)
    #HTTP endpoint: /polls/api/set-id/?id=<id>

    #Reads `id` from query params and sets it as the current binary ID.
    #Returns 400 if id is missing, otherwise 200 with a success message.
    #not needed since it is certain that the id is being received from the scanner
    if not binary_id:
        return JsonResponse({"error": "Missing id parameter"}, status=400)

    #make dedicated function to validate id.   
    data = getpath(binary_id)
    if "Error" in data:
        #decide what to add for the placeholder
        return JsonResponse({"error: placeholder"}, status=404)

    CURRENT_BIN_ID = binary_id 

    ID_RECEIVED_ONCE = True


    return JsonResponse({"message": f"Successful. Binary ID set to {CURRENT_BIN_ID}"}, 
    status=200)


 #Reset the flag to allow re-calling receiveBinId
def restartflag(request):
    global ID_RECEIVED_ONCE
    ID_RECEIVED_ONCE = False
    return JsonResponse({"message": "Flag reset successfully"}, status=200)

