from ariadne import ObjectType, MutationType, make_executable_schema, gql
from apps.movies.models import Actor, Movie

type_defs = gql("""
              type Actor {
                id: ID!
                name: String!
              }

              type Movie {
                id: ID!
                title: String!
                actors: [Actor]
                year: Int!
              }
              
              type Query {
                actor(id: ID!): Actor
                movie(id: ID!): Movie
                actors: [Actor]
                movies: [Movie]
              }
              
              input ActorInput {
                id: ID
                name: String!
              }
              
              input MovieInput {
                id: ID
                title: String
                actors: [ActorInput]
                year: Int
              }
              
              type ActorPayload {
                ok: Boolean
                actor: Actor
              }
              
              type MoviePayload {
                ok: Boolean
                movie: Movie
              }
              
              type Mutation {
                createActor(input: ActorInput): ActorPayload
                createMovie(input: MovieInput): MoviePayload
                updateActor(id: ID!, input: ActorInput): ActorPayload
                updateMovie(id: ID!, input: MovieInput): MoviePayload
              }
            """)

query = ObjectType('Query')
actor = ObjectType('Actor')
movie = ObjectType('Movie')

@query.field('actors')
def resolve_actors(_, info):
  actors = Actor.objects.all()
  return actors

@query.field('actor')
def resolve_actor(_, info, id):
  actor = Actor.objects.get(pk=id)
  return actor

@query.field('movies')
def resolve_movies(_, info):
  movies = Movie.objects.all()
  return movies

@query.field('movie')
def resolve_movie(_, info, id):
  movie = Movie.objects.get(pk=id)
  return movie
 
@movie.field('actors')
def resolve_movie_actors(_, info):
  movie = Movie.objects.get(title=_)
  return movie.actors.all()

'''
  Mutation 
'''

mutation = MutationType()

@mutation.field('createActor')
def resolve_create_actor(_, info, input):  
  try:
    newActor = Actor(name=input["name"])
    newActor.save()
    return {
      "ok": True,
      "actor": newActor,
    }
  except ValidationError as err:
    return {
      "ok": False,
      "name": 'undefined'
    }

@mutation.field('createMovie')
def resolve_create_movie(_, info, input):
  try:
    newMovie = Movie(title=input["title"])
    newMovie.year = input["year"]
    
    actors = []
    idActors = [actor["id"] for actor in input["actors"]]
    for id in idActors:
      actor = Actor.objects.get(pk=id)
      actors.append(actor)
    newMovie.save()
    newMovie.actors.set(actors)
    
    
    return {
      "ok": True,
      "movie": newMovie,
    }
  except:
    return {
      "ok": input,
      "movie": 'undefined',
    }

@mutation.field('updateActor')
def resolve_update_actor(_, info, input):
  pass

@mutation.field('updateMovie')
def resolve_update_movie(_, info, input):
  pass
 
schema = make_executable_schema(type_defs, [query, actor, movie, mutation])
 
