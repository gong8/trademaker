class STATUS():
  """
  Status code for HTTP error responses.
  Client errors should be in the form 4xx.
  Server error codes are in the form 5xx.
  Existing error codes: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
  """

  OK = 200
  BAD_REQUEST = 400
  POLYGON_ERROR = 521
  SIMULATOR_ERROR = 522