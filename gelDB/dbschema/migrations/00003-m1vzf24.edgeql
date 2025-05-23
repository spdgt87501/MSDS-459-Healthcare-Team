CREATE MIGRATION m1vzf24ipx7mpi6mrhueie4yc7iz7ym4ffbpkg2m37zxejxednxtvq
    ONTO m1vrb3s7b255lzglllbssfbswprcqb2xp2xhycqo37kqqogj4taq2a
{
  ALTER TYPE default::Relation {
      DROP PROPERTY object;
  };
  ALTER TYPE default::Relation {
      CREATE REQUIRED LINK object: default::Entity {
          SET REQUIRED USING (SELECT
              default::Entity FILTER
                  (.name = 'UNKNOWN_ENTITY')
          LIMIT
              1
          );
      };
  };
  ALTER TYPE default::Relation {
      DROP PROPERTY subject;
  };
  ALTER TYPE default::Relation {
      CREATE REQUIRED LINK subject: default::Entity {
          SET REQUIRED USING (SELECT
              default::Entity FILTER
                  (.name = 'UNKNOWN_ENTITY')
          LIMIT
              1
          );
      };
  };
};
