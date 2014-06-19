BearForm
========
Easy data conversion and validation for frontends. BearForm is expected to be
useful primarily as part of an API endpoint. Processing deserialized JSON,
YAML, or whatever flavor you prefer is what it's good at.

[![Build Status](https://travis-ci.org/WiFast/bearform.svg)](https://travis-ci.org/WiFast/bearform)

Example
-------
BearForm works like a lot of form validators in that you declare Form classes to define a data schema. For example:

    from bearform import Form, Field

    class BearForm(Form):
        name = Field(str)
        type = Field(str)
        height = Field(float)

Let's say someone's POSTing bears to a Flask view. You might use it like this:

    from bearform import FormError

    @app.route("/bear")
    def bear():
        if request.is_json:
            try:
                data = request.get_json()
                bear = BearForm.decode(data)
                bear.validate()
                msg = "this is a {} bear".format(bear.type)
                return jsonify({'status': 'success', 'msg': 'msg'})
            except FormError as e:
                return jsonify({'status': 'fail', 'error': str(e)}), 400
        else:
            return jsonify({'status': 'fail', 'error': 'invalid request'}), 400

The other direction works, too. Lets modify our view to return a small grizzly
bear named Fluffy when no JSON is posted:

    @app.route("/bear")
    def bear():
        if request.is_json:
            try:
                data = request.get_json()
                bear = BearForm.decode(data)
                bear.validate()
                msg = "this is a {} bear".format(bear.type)
                return jsonify({'status': 'success', 'msg': 'msg'})
            except FormError as e:
                return jsonify({'status': 'fail', 'error': str(e)}), 400
        else:
            bear = BearForm(name='Fluffy', type='grizzly', height=6.3)
            return jsonify(bear.encode())

BearForm gives you three ways to get the data out of a populated form object:
attribute access, the to_dict method, and the to_object method. You've seen
attribute access used in the above examples. The to_dict method does the
obvious thing: it returns the form as a dictionary. The to_obj method is more
interesting as it can populate an existing object with decoded data stored in a
form object. Let's say we have a Bear document (built with BearField, appropriately):

    from bearfield import Document, Field

    class Bear(Document):
        class Meta:
            connection = 'bears'
        name = Field(str)
        type = Field(str)
        height = Field(float)

That looks oddly familiar... Lets decode some data and save it to the database:

    data = {'name': 'Fluffy', 'type': 'grizzly', height: '6.3'}
    bear_form = BearForm.decode(data)
    bear = Bear()
    bear_form.to_obj(bear)
    bear.save()

Easy, yes? Since decode returns a form object and to_obj returns the object we
passed to it we can shorten the example to this:
    
    data = {'name': 'Fluffy', 'type': 'grizzly', height: '6.3'}
    BearForm.decode(data).to_obj(Bear()).save()

Expect even better BearField integration in the future.

But what about validation? Including validators on fields is straightforward:

    from bearform import ValidationError

    def is_not_empty(cls, name, value):
        if not value:
            raise ValidationError("{} cannot be empty".format(name))

    def is_positive(cls, name, value):
        if value <= 0:
            raise ValidationError("{} must be a positive value".format(name))

    class BearForm(form):
        name = Field(str, validators=[is_not_empty])
        type = Field(str)
        height = Field(float, validators=[is_positive])

Now during decoding a ValidationError will be raised of the name is empty or
the bear does not have a positive height.

License
-------
Copyright (c) 2014 WiFast, Inc. This project and all of its contents is licensed under the
BSD-derived license as found in the included [LICENSE][1] file.

[1]: https://github.com/WiFast/bearform/blob/master/LICENSE "LICENSE"
