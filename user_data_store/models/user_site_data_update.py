# coding: utf-8

"""
    User Data API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class UserSiteDataUpdate(object):
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
        'consented_at': 'datetime',
        'blocked': 'bool',
        'data': 'object'
    }

    attribute_map = {
        'consented_at': 'consented_at',
        'blocked': 'blocked',
        'data': 'data'
    }

    def __init__(self, consented_at=None, blocked=None, data=None):  # noqa: E501
        """UserSiteDataUpdate - a model defined in Swagger"""  # noqa: E501

        self._consented_at = None
        self._blocked = None
        self._data = None
        self.discriminator = None

        if consented_at is not None:
            self.consented_at = consented_at
        if blocked is not None:
            self.blocked = blocked
        if data is not None:
            self.data = data

    @property
    def consented_at(self):
        """Gets the consented_at of this UserSiteDataUpdate.  # noqa: E501


        :return: The consented_at of this UserSiteDataUpdate.  # noqa: E501
        :rtype: datetime
        """
        return self._consented_at

    @consented_at.setter
    def consented_at(self, consented_at):
        """Sets the consented_at of this UserSiteDataUpdate.


        :param consented_at: The consented_at of this UserSiteDataUpdate.  # noqa: E501
        :type: datetime
        """

        self._consented_at = consented_at

    @property
    def blocked(self):
        """Gets the blocked of this UserSiteDataUpdate.  # noqa: E501


        :return: The blocked of this UserSiteDataUpdate.  # noqa: E501
        :rtype: bool
        """
        return self._blocked

    @blocked.setter
    def blocked(self, blocked):
        """Sets the blocked of this UserSiteDataUpdate.


        :param blocked: The blocked of this UserSiteDataUpdate.  # noqa: E501
        :type: bool
        """

        self._blocked = blocked

    @property
    def data(self):
        """Gets the data of this UserSiteDataUpdate.  # noqa: E501


        :return: The data of this UserSiteDataUpdate.  # noqa: E501
        :rtype: object
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this UserSiteDataUpdate.


        :param data: The data of this UserSiteDataUpdate.  # noqa: E501
        :type: object
        """

        self._data = data

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
        if not isinstance(other, UserSiteDataUpdate):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
