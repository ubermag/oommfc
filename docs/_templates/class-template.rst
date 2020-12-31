{{ objname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :special-members:

   .. raw:: html

      <hr>

   {% block methods %}
   {% if methods %}
   .. rubric:: {{ ('Methods') }}

   .. autosummary::
      :nosignatures:
   {% for item in all_methods %}
      {% if not item.startswith('_') or
         (item.startswith('__') and item not in excluded_members) %}
         ~{{ name }}.{{ item }}
      {% endif %}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ ('Properties') }}

   .. autosummary::
   {% for item in attributes %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   .. raw:: html

      <hr>
