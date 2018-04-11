# coding: utf-8

"""
    Access Control API

    # The Access Control API  ## Overview The Access Control API is an API exposed to other core components. It uses an API Key in an HTTP header to perform authentication and authorisation.  Most of the API calls facilitates CRUD of the entities defined in the Access Control component. Others calls allows the retrieval of information in a form that is convenient for other components (most notably the Management Layer) to consume.   # noqa: E501

    OpenAPI spec version: 
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class DomainRole(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'domain_id': 'int',
        'role_id': 'int',
        'grant_implicitly': 'bool',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    }

    attribute_map = {
        'domain_id': 'domain_id',
        'role_id': 'role_id',
        'grant_implicitly': 'grant_implicitly',
        'created_at': 'created_at',
        'updated_at': 'updated_at'
    }

    def __init__(self, domain_id=None, role_id=None, grant_implicitly=None, created_at=None, updated_at=None):  # noqa: E501
        """DomainRole - a model defined in Swagger"""  # noqa: E501

        self._domain_id = None
        self._role_id = None
        self._grant_implicitly = None
        self._created_at = None
        self._updated_at = None
        self.discriminator = None

        self.domain_id = domain_id
        self.role_id = role_id
        self.grant_implicitly = grant_implicitly
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def domain_id(self):
        """Gets the domain_id of this DomainRole.  # noqa: E501


        :return: The domain_id of this DomainRole.  # noqa: E501
        :rtype: int
        """
        return self._domain_id

    @domain_id.setter
    def domain_id(self, domain_id):
        """Sets the domain_id of this DomainRole.


        :param domain_id: The domain_id of this DomainRole.  # noqa: E501
        :type: int
        """
        if domain_id is None:
            raise ValueError("Invalid value for `domain_id`, must not be `None`")  # noqa: E501

        self._domain_id = domain_id

    @property
    def role_id(self):
        """Gets the role_id of this DomainRole.  # noqa: E501


        :return: The role_id of this DomainRole.  # noqa: E501
        :rtype: int
        """
        return self._role_id

    @role_id.setter
    def role_id(self, role_id):
        """Sets the role_id of this DomainRole.


        :param role_id: The role_id of this DomainRole.  # noqa: E501
        :type: int
        """
        if role_id is None:
            raise ValueError("Invalid value for `role_id`, must not be `None`")  # noqa: E501

        self._role_id = role_id

    @property
    def grant_implicitly(self):
        """Gets the grant_implicitly of this DomainRole.  # noqa: E501


        :return: The grant_implicitly of this DomainRole.  # noqa: E501
        :rtype: bool
        """
        return self._grant_implicitly

    @grant_implicitly.setter
    def grant_implicitly(self, grant_implicitly):
        """Sets the grant_implicitly of this DomainRole.


        :param grant_implicitly: The grant_implicitly of this DomainRole.  # noqa: E501
        :type: bool
        """
        if grant_implicitly is None:
            raise ValueError("Invalid value for `grant_implicitly`, must not be `None`")  # noqa: E501

        self._grant_implicitly = grant_implicitly

    @property
    def created_at(self):
        """Gets the created_at of this DomainRole.  # noqa: E501


        :return: The created_at of this DomainRole.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this DomainRole.


        :param created_at: The created_at of this DomainRole.  # noqa: E501
        :type: datetime
        """
        if created_at is None:
            raise ValueError("Invalid value for `created_at`, must not be `None`")  # noqa: E501

        self._created_at = created_at

    @property
    def updated_at(self):
        """Gets the updated_at of this DomainRole.  # noqa: E501


        :return: The updated_at of this DomainRole.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this DomainRole.


        :param updated_at: The updated_at of this DomainRole.  # noqa: E501
        :type: datetime
        """
        if updated_at is None:
            raise ValueError("Invalid value for `updated_at`, must not be `None`")  # noqa: E501

        self._updated_at = updated_at

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, DomainRole):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other