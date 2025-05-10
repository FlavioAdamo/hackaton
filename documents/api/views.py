from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import DriveFileSerializer, SearchSerializer
from documents.views import search_similar_chunks
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from services.generate.generate import generate_llm_response


class DocumentSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get("query")
        translated_query = generate_llm_response(
            f"Create a standalone question in english from the following text: {query}"
        )
        similar_chunks = search_similar_chunks(translated_query, limit=3)
        print(similar_chunks)
        if not similar_chunks:
            return Response(
                {"message": "No similar documents found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # return Response(DocumentChunkSerializer(similar_chunks, many=True).data)
        # return Response([chunk.document.id for chunk in similar_chunks])
        # first_doc_id = similar_chunks[0].document.id
        # document = DocumentContent.objects.filter(id=first_doc_id).first()
        # if not document:
        #     return Response(
        #         {"message": "Document not found"},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        # return Response(DriveFileSerializer(document.drive_file).data)

        # return Response(DocumentChunkSerializer(similar_chunks, many=True).data)
        # print(similar_chunks[0].content)
        documents = []
        for chunk in similar_chunks:
            if chunk.document not in documents:
                documents.append(chunk.document)

        print([document.drive_file.id for document in documents])
        drive_files = [document.drive_file for document in documents]

        # document_ids = set([chunk.document.id for chunk in similar_chunks])
        # similar_doc_id = next(
        #     iter(document_ids)
        # )  # Get first element from set using iter()

        # similar_documents = DocumentContent.objects.filter(id__in=document_ids)

        # print(similar_documents)

        res = {"file": drive_files[0], "message": "contenuto messaggio ai"}
        serializer = SearchSerializer(instance=res)
        return Response(serializer.data)

        drive_files = DriveFileSerializer(drive_files, many=True).data

        return Response(drive_files)


class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get("query")
        response = generate_llm_response(query)
        return Response(response)
