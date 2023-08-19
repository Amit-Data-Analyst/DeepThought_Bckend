# events/views.py

from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Event
from .serializers import EventSerializer
from rest_framework import viewsets, status

class EventPagination(PageNumberPagination):
    page_size = 10  # Number of events per page
    page_size_query_param = 'limit'
    max_page_size = 100

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @action(detail=False, methods=['GET'])
    def list_events(self, request):
        event_type = request.query_params.get('type')
        page = int(request.query_params.get('page', 1))

        if event_type == 'latest':
            now = timezone.now()
            events = Event.objects.filter(schedule__lte=now).order_by('-schedule')
        else:
            events = self.queryset

        paginator = EventPagination()
        page_events = paginator.paginate_queryset(events, request)
        serializer = self.get_serializer(page_events, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['GET'])
    def retrieve_event(self, request, pk=None):
        event = self.get_object()
        serializer = self.get_serializer(event)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def create_event(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            return Response({'id': event.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def delete_event(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
