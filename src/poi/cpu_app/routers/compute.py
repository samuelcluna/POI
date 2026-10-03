from fastapi import APIRouter, Query

from poi.cpu_app.services import compute

router = APIRouter(tags=["cpu"])


@router.get("/primes")
def primes(limit: int = Query(50_000, ge=2, le=500_000)):
    return {"limit": limit, "primes": compute.count_primes(limit)}


@router.get("/sort")
def sort(n: int = Query(200_000, ge=1, le=2_000_000), seed: int = 42):
    return {"n": n, **compute.sort_numbers(n, seed)}


@router.get("/matrix")
def matrix(size: int = Query(100, ge=1, le=300), seed: int = 42):
    return {"size": size, "trace": compute.matrix_trace(size, seed)}


@router.get("/hash")
def hash_(iterations: int = Query(150_000, ge=1, le=5_000_000)):
    return {"iterations": iterations, "digest": compute.pbkdf2(iterations)}
