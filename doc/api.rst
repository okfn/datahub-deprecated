Web programming interface
=========================

datahub features a somewhat RESTful, JSON-based API. While we're generally
exposing resources in a style conformant with REST principles, two deviations
from the strict paradigm were made:

* The API is mounted outside of the user-facing actions, mainly in order to
  support versioning.
* Few hypermedia links are provided within the API, a client has to compose 
  those from the other given data (no HATEOAS).

Authentication
--------------

Authentication is performed using HTTP Basic authentication. Basic headers must
include a valid username and password combination as used in the web user
interface. In future versions, both API keys and OAuth authorization may be 
supported.

Identifiers
-----------

Most entities managed by the datahub have both a human-readable name and a
database identifier. While the identifier is often emitted from the API, it
cannot be used to retrieve entities: all API calls use human-readable names.

Error Messages
--------------

Errors within the API will always return a non-2xx/3xx HTTP status code (but
not all such codes indicate errors; e.g. HTTP 410 is used to indicate the
successful deletion of an entity). An error message from the API is always 
JSON-formatted and has the following fields:

* **status**: the HTTP status code, repeated.
* **name**: the name of the error message.
* **description**: a short description of the error condition.

For form validation errors, an additional key, **errors** is supplied,
containing a mapping of all failing fields to their individual error messages.

Account API
-----------

User profiles can both be read and - if authorized - be updated via the web
interface. Lisiting users and API-based registration is not supported.

* **GET /api/v1/account/{account}**: retrieve a user profile, either for a
  normal user or an organization account.
* **PUT /api/v1/account/{account}**: update the account settings with a JSON
  or form set of data fields. Supported fields:

  * **name**: the user or organisation name.
  * **full_name**: a longer version of the name, e.g. a normal surname/name.
  * email: an email address (needs to be verified to be fully enabled).

Resource API
------------

Resources are references to remote or uploaded files and API endpoints. The
resource API handles metadata aspects of resource management, not the data
itself.

* **GET /api/v1/resource/{owner}**: Retrieve a listing of all resources
  managed by the given account. This returns full JSON representations of the 
  resources and does not currently support pagination.
* **GET /api/v1/resource/{owner}/{resource}**: Return a single resource as a
  JSON representation.
* **POST /api/v1/resource/{owner}**: Create a new resource. The owner is
  generally expected to also be the authenticated user. If successful, this 
  operation will generate a 302 HTTP forward to the newly created resource.
  Supported fields:

  * **name**: the name of the resource, unique for this user. This name is
    expected to consist only of alphanumeric characters, dashes and 
    underscores and it must start with an alphanumeric character.
  * **url**: the URL of the resource. This should generally point at the 
    resource itself rather than at any listings, info pages or boilerplate
    licenses.
  * **summary**: a short text describing this resource (more like a title than
    actual data documentation).
  * meta: mapping object, giving arbitrary, additional metadata as a mapping.

* **PUT /api/v1/resource/{owner}/{resource}**: Update resource metadata. This 
  requires the user to be authorized to edit the resource - in general this 
  applies only to one's own resources. The supported fields match those 
  of the creation operation; renames are supported at any time but strongly 
  discouraged. If successful, this operation will returned the modified 
  resource object.
* **DELETE /api/v1/resource/{owner}/{resource}**: Delete a resource from the 
  database. If successful, this operation will return a HTTP 410 Gone error
  message.

Dataset API
-----------

Datasets are groupings of related resources that have a name and brief
description. Their API also handles the management of the many-to-many
association between resources and datasets.

* **GET /api/v1/dataset/{owner}**: Retrieve a listing of all datasets
  managed by the given account. This returns full JSON representations of the 
  datasets and does not currently support pagination.
* **GET /api/v1/dataset/{owner}/{dataset}**: Return a single dataset as a
  JSON representation.
* **POST /api/v1/dataset/{owner}**: Create a new dataset. The owner is
  generally expected to also be the authenticated user. If successful, this 
  operation will generate a 302 HTTP forward to the newly created dataset.
  Supported fields:

  * **name**: the name of the dataset, unique for this user. This name is
    expected to consist only of alphanumeric characters, dashes and 
    underscores and it must start with an alphanumeric character.
  * **summary**: a short text describing this dataset (more like a title than
    actual data documentation).
  * meta: mapping object, giving arbitrary, additional metadata as a mapping.

* **PUT /api/v1/dataset/{owner}/{dataset}**: Update dataset metadata. This 
  requires the user to be authorized to edit the dataset. The supported 
  fields match those of the creation operation; renames are supported at any 
  time but strongly discouraged. If successful, this operation will returned 
  the modified dataset object.
* **GET /api/v1/dataset/{owner}/{dataset}/resources**: List all resources 
  within the given dataset. This will yield the fully representation of all
  contained resources and does not currently support pagination.
* **POST /api/v1/dataset/{owner}/{dataset}/resources**: Add a resource to the
  dataset, if authorized. This expects the following information about the
  resource:

  * **owner**: the owner of the resource that is to be added. May be any user,
    this does not imply authorization to edit the resource. 
  * **name**: name of the resource, name changes do not break this association.

* **DELETE /api/v1/dataset/{owner}/{dataset}/resources/{resource_owner}/{resource_name}**: 
  Remove a resource from the dataset, if authorized. Note that this resource is
  virtual in the sense that a GET request to check membership is not supported.
* **DELETE /api/v1/dataset/{owner}/{dataset}**: Delete a dataset from the 
  database. If successful, this operation will return a HTTP 410 Gone error
  message.

Event API
---------

Events are generated whenever a user performs a noteworthy action within the
system. They may be associated with one or many other domain objects, such as
users, resources or datasets though an association called an event stream.
Users can subscribe to the event streams of other objects in order to recieve
update messages in their dashboard whenever some operation has been performed
on the respective domain object.

* **GET /api/v1/event/{event}**: Unlike all other objects in the system, events
  don't have a name and are addressed by database identifier. This returns a
  JSON representation of the event. Event IDs can be found, amongst other
  places, in the Atom field generated for domain objects.
* **GET /api/v1/stream/{type}/{id}**: Returns the last 50 events in a given
  event stream. This does not at the moment support pagination to go further
  back in history. The ID is the database identifier of the affected domain
  object, and the type one of: node (for both datasets and resources), account.


