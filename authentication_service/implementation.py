from authentication_service.api.stubs import AbstractStubClass


class Implementation(AbstractStubClass):

    @staticmethod
    def client_list(request, offset=None, limit=None, client_ids=None,
                    client_id=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    @staticmethod
    def client_read(request, client_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param client_id: string A string value identifying the client
        """
        raise NotImplementedError()

    @staticmethod
    def user_list(request, offset=None, limit=None, email=None,
                  username_prefix=None, user_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    @staticmethod
    def user_delete(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        raise NotImplementedError()

    @staticmethod
    def user_read(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        raise NotImplementedError()

    @staticmethod
    def user_update(request, body, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: dict A dictionary containing the parsed and validated body
        :param user_id: string A UUID value identifying the user.
        """
        raise NotImplementedError()