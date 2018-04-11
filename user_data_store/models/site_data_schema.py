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


class SiteDataSchema(object):
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
        'site_id': 'int',
        'schema': 'object',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    }

    attribute_map = {
        'site_id': 'site_id',
        'schema': 'schema',
        'created_at': 'created_at',
        'updated_at': 'updated_at'
    }

    def __init__(self, site_id=None, schema=None, created_at=None, updated_at=None):  # noqa: E501
        """SiteDataSchema - a model defined in Swagger"""  # noqa: E501

        self._site_id = None
        self._schema = None
        self._created_at = None
        self._updated_at = None
        self.discriminator = None

        self.site_id = site_id
        self.schema = schema
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def site_id(self):
        """Gets the site_id of this SiteDataSchema.  # noqa: E501


        :return: The site_id of this SiteDataSchema.  # noqa: E501
        :rtype: int
        """
        return self._site_id

    @site_id.setter
    def site_id(self, site_id):
        """Sets the site_id of this SiteDataSchema.


        :param site_id: The site_id of this SiteDataSchema.  # noqa: E501
        :type: int
        """
        if site_id is None:
            raise ValueError("Invalid value for `site_id`, must not be `None`")  # noqa: E501

        self._site_id = site_id

    @property
    def schema(self):
        """Gets the schema of this SiteDataSchema.  # noqa: E501


        :return: The schema of this SiteDataSchema.  # noqa: E501
        :rtype: object
        """
        return self._schema

    @schema.setter
    def schema(self, schema):
        """Sets the schema of this SiteDataSchema.


        :param schema: The schema of this SiteDataSchema.  # noqa: E501
        :type: object
        """
        if schema is None:
            raise ValueError("Invalid value for `schema`, must not be `None`")  # noqa: E501

        self._schema = schema

    @property
    def created_at(self):
        """Gets the created_at of this SiteDataSchema.  # noqa: E501


        :return: The created_at of this SiteDataSchema.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this SiteDataSchema.


        :param created_at: The created_at of this SiteDataSchema.  # noqa: E501
        :type: datetime
        """
        if created_at is None:
            raise ValueError("Invalid value for `created_at`, must not be `None`")  # noqa: E501

        self._created_at = created_at

    @property
    def updated_at(self):
        """Gets the updated_at of this SiteDataSchema.  # noqa: E501


        :return: The updated_at of this SiteDataSchema.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this SiteDataSchema.


        :param updated_at: The updated_at of this SiteDataSchema.  # noqa: E501
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
        if not isinstance(other, SiteDataSchema):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
