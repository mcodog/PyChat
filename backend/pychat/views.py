import json
from bson import ObjectId
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.conf import settings
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from g4f.client import Client

client = Client()


def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        # Add any other necessary parameters
    )
    return response.choices[0].message.content

chat_with_gpt("Hello there, what is your name?")

db = settings.MONGO_DB
chats_collection = db['chats']
messages_collection = db['messages']

@method_decorator(csrf_exempt, name='dispatch')
class ChatListView(View):
    def get(self, request):
        chats = chats_collection.find()  
        chat_list = []

        for chat in chats:
            chat['_id'] = str(chat['_id'])  
            # chat['messages'] = [{**msg, '_id': str(msg['_id'])} for msg in chat.get('messages', [])]  # Convert message IDs to string
            chat_list.append(chat)

        return JsonResponse({"chats": chat_list}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class ChatListCreateView(View):
    def post(self, request):
        data = json.loads(request.body)
        
        if "chat_name" not in data:
            return JsonResponse({"error": "Chat name is required."}, status=400)

        new_chat = {
            "chat_name": data["chat_name"],
            "timestamp": timezone.now(),
            "messages": []
        }
        
        result = chats_collection.insert_one(new_chat)
        new_chat["_id"] = str(result.inserted_id)
        return JsonResponse(new_chat, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class ChatMessageCreateView(View):
    def post(self, request, chat_id):
        data = json.loads(request.body)
        
        if "message" not in data or "sender" not in data:
            return JsonResponse({"error": "Message and sender are required."}, status=400)

        chat = chats_collection.find_one({"_id": ObjectId(chat_id)})
        if not chat:
            return JsonResponse({"error": "Chat not found."}, status=404)

        new_message = {
            "_id": str(ObjectId()),
            "message": data["message"],
            "sender": data["sender"],
            "timestamp": timezone.now()
        }

        edit_message = {
            "original_message_id": new_message["_id"],
            "message": data["message"]
        }

        result = chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": new_message}}
        )

        if result.modified_count:
            new_message["_id"] = str(result.upserted_id)
            return self.trigger_message_edit(request, chat_id, edit_message)
        else:
            return JsonResponse({"error": "Failed to add message."}, status=500)

    def trigger_message_edit(self, request, chat_id, data):
        if "original_message_id" not in data or "message" not in data:
            return JsonResponse({"error": "Original message ID and new message content are required."}, status=400)
        
        chat = chats_collection.find_one({"_id": ObjectId(chat_id)})
        if not chat:
            return JsonResponse({"error": "Chat not found."}, status=404)

        original_message = None
        for msg in chat['messages']:
            if "_id" in msg and str(msg['_id']) == data["original_message_id"]:
                original_message = msg
                break

        if not original_message:
            return JsonResponse({"error": "Original message not found."}, status=404)
        
        gpt_response = chat_with_gpt(original_message["message"])
        print("gpt:", gpt_response)
        new_message = {
            "message": gpt_response,
            "sender": "PyChat",
            "timestamp": timezone.now()
        }

        result = chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": new_message}}
        )

        if result.modified_count:
            new_message["_id"] = str(result.upserted_id)
            return JsonResponse(new_message, status=201)
        else:
            return JsonResponse({"error": "Failed to add new message."}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class ChatMessageEditView(View):
    def post(self, request, chat_id):
        data = json.loads(request.body)
        
        if "original_message_id" not in data or "message" not in data:
            return JsonResponse({"error": "Original message ID and new message content are required."}, status=400)
        
        chat = chats_collection.find_one({"_id": ObjectId(chat_id)})
        if not chat:
            return JsonResponse({"error": "Chat not found."}, status=404)
        
        original_message = next((msg for msg in chat['messages'] if str(msg['_id']) == data["original_message_id"]), None)
        if not original_message:
            return JsonResponse({"error": "Original message not found."}, status=404)
        
        new_message = {
            "message": data["message"] if data["message"] else original_message["message"],
            "sender": "PyChat",
            "timestamp": timezone.now()
        }

        result = chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": new_message}}
        )

        if result.modified_count:
            new_message["_id"] = str(result.upserted_id)
            return JsonResponse(new_message, status=201)
        else:
            return JsonResponse({"error": "Failed to add new message."}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ChatDetailView(View):
    def get(self, request, chat_id):
        chat = chats_collection.find_one({"_id": ObjectId(chat_id)})
        if chat:
            chat['_id'] = str(chat['_id'])
            return JsonResponse({
                "chat_name": chat["chat_name"],
                "messages": chat["messages"],
                "timestamp": chat["timestamp"]
            })
        else:
            return JsonResponse({"error": "Chat not found."}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class ChatDeleteView(View):
    def delete(self, request, chat_id):
        result = chats_collection.delete_one({"_id": ObjectId(chat_id)})
        if result.deleted_count:
            return JsonResponse({"message": "Chat deleted successfully."}, status=204)
        else:
            return JsonResponse({"error": "Chat not found."}, status=404)
