import abc

class TemplateEngine(object):

    @abc.abstractmethod
    def template_from_file(self, file_path):
        raise NotImplementedError

    @abc.abstractproperty
    def name(self):
        raise NotImplementedError