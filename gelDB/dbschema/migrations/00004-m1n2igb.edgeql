CREATE MIGRATION m1n2igb5fvyx7cor64zw432qh7ifqirq6f7zwzff5oprfp7cqdyrxq
    ONTO m1vzf24ipx7mpi6mrhueie4yc7iz7ym4ffbpkg2m37zxejxednxtvq
{
  ALTER TYPE default::Relation {
      DROP LINK object;
  };
  ALTER TYPE default::Relation {
      DROP LINK subject;
  };
  ALTER TYPE default::Relation {
      CREATE REQUIRED PROPERTY object: std::str {
          SET REQUIRED USING (<std::str>'UNKNOWN_OBJECT');
      };
  };
  ALTER TYPE default::Relation {
      CREATE REQUIRED PROPERTY subject: std::str {
          SET REQUIRED USING (<std::str>'UNKNOWN_SUBJECT');
      };
  };
};
