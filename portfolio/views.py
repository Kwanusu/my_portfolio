from rest_framework import viewsets, permissions, status
from .models import Message, SystemLog
from .serializers import MessageSerializer, SystemLogSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import Message 
from .serializers import MessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer

    def get_permissions(self):
        # Anyone can send a message (Public Contact Form)
        if self.action == 'create':
            return [permissions.AllowAny()]
        # Only Joseph (Admin) can view/delete/edit messages
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {"message": "Transmission Received. I'll get back to you shortly."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SystemLogViewSet(viewsets.ModelViewSet):
    """
    Handles System Monitoring.
    Admin Only access.
    """
    queryset = SystemLog.objects.all().order_by('-timestamp')
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAdminUser]           

class MessageReplyView(APIView):
    def post(self, request, pk):
        try:
            # Match your model's specific field: Message
            msg_obj = Message.objects.get(pk=pk)
            reply_body = request.data.get('reply_body')

            if not reply_body:
                return Response({"error": "Reply payload is empty"}, status=status.HTTP_400_BAD_REQUEST)

            # Transmission Logic
            subject = f"Re: {msg_obj.subject}"
            email_content = f"Hello {msg_obj.sender_name},\n\n{reply_body}\n\n---\nTechnical Support\nJoseph Kwanusu"
            
            send_mail(
                subject,
                email_content,
                settings.DEFAULT_FROM_EMAIL,
                [msg_obj.sender_email],
                fail_silently=False,
            )

            # Update status to reflected it has been dealt with
            msg_obj.is_read = True
            msg_obj.is_replied = True # This ensures the frontend 'Pending' switches to 'Replied' 
            msg_obj.save()

            return Response({"status": "Transmission Successful"}, status=status.HTTP_200_OK)

        except Message.DoesNotExist:
            return Response({"error": "Message ID not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)