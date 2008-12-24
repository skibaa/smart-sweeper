from google.appengine.ext import db

class CachedReferenceProperty(db.ReferenceProperty):

  def __property_config__(self, model_class, property_name):
    super(CachedReferenceProperty, self).__property_config__(model_class,
                                                       property_name)
    #Just carelessly override what super made
    setattr(self.reference_class,
            self.collection_name,
            _CachedReverseReferenceProperty(model_class, property_name,
                self.collection_name))

class _CachedReverseReferenceProperty(db._ReverseReferenceProperty):

    def __init__(self, model, prop, collection_name):
        super(_CachedReverseReferenceProperty, self).__init__(model, prop)
        self.__collection_name = collection_name

    def __get__(self, model_instance, model_class):
        if model_instance is None:
            return self
        if self.__collection_name in model_instance.__dict__:# why does it get here at all?
            return model_instance.__dict__[self.__collection_name]

        query=super(_CachedReverseReferenceProperty, self).__get__(model_instance,
            model_class)
        #replace the attribute on the instance
        res=[c for c in query]
        model_instance.__dict__[self.__collection_name]=res
        return res

    def __delete__ (self, model_instance):
        if model_instance is not None:
            del model_instance.__dict__[self.__collection_name]

