from django.shortcuts import render
from ares import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ares import serializers

class handleConstraints(APIView):
    def get(self, request, format=None):
        constraints = models.Constraints.objects.all()
        serializer = serializers.constraintSerializer(constraints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = serializers.constraintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            constraint = models.Constraints.objects.get(pk=pk)
        except models.Constraints.DoesNotExist:
            return Response({"error": "Constraint not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.constraintSerializer(constraint, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

