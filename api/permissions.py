from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):

	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.is_superuser
	def has_object_permission(self,request,view,obj):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.is_superuser


class IsAuthorOrReadonly(permissions.BasePermission):

	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True

		return request.user.is_authenticated and request.user.is_author 

	def has_object_permission(self, request, view,obj):
		if request.method in permissions.SAFE_METHODS:
			return True

		return obj.author== request.user 



