from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import selectinload

# Tworzenie aplikacji FastAPI
app = FastAPI()

# Konfiguracja połączenia z bazą danych SQLite (tworzymy tymczasową bazę w pamięci)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Deklaracja bazowego modelu
Base = declarative_base()

# Definicja modelu Elf
class Elf(Base):
    __tablename__ = "elves"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    paternity_or_maternity = Column(Boolean, default=False)
    packages = relationship("Package", back_populates="assigned_to")

# Definicja modelu Package
class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    elf_id = Column(Integer, ForeignKey("elves.id"))
    assigned_to = relationship("Elf", back_populates="packages")

# Tworzenie tabel w bazie danych
Base.metadata.create_all(bind=engine)

# Utworzenie sesji do interakcji z bazą danych
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Zwrócenie sesji bazy danych
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Endpointy dla zarządzania elfami
@app.post("/elves/")
def create_elf(name: str, status: str, db: Session = Depends(get_db)):
    try:
        db_elf = Elf(name=name, status=status)
        db.add(db_elf)
        db.commit()
        db.refresh(db_elf)
        return {"id": Elf.id, "name": Elf.name, "elf id": Elf.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/elves/{elf_id}")
def read_elf(elf_id: int, db: Session = Depends(get_db)):
    db_elf = db.query(Elf).filter(Elf.id == elf_id).first()
    if db_elf is None:
        raise HTTPException(status_code=404, detail="Elf not found")
    db.close()
    return db_elf
    

# Endpointy dla zarządzania paczkami
@app.post("/packages/")
def create_package(name: str, elf_id: int, db: Session = Depends(get_db)):
    try:
        db_package = Package(name=name, elf_id=elf_id)
        db.add(db_package)
        db.commit()
        db.refresh(db_package)
        return {"package": Package.name}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.put("/assign-package/{package_id}/{elf_id}")
def assign_package(package_id: int, elf_id: int, db: Session = Depends(get_db)):
    db_package = db.query(Package).filter(Package.id == package_id).first()
    if db_package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    db_package.elf_id = elf_id
    db.commit()
    db.close()
    return {"message": f"Package {package_id} assigned to Elf {elf_id}"}

@app.put("/give_paternity_or_maternity/{elf_id}/")
async def give_paternity_or_maternity(elf_id: int, paternity_or_maternity: bool, db: Session = Depends(get_db)):
    try:
        elf = db.query(Elf).filter(Elf.id == elf_id).first()
        if not elf:
            raise HTTPException(status_code=404, detail="Elf not found")

        elf.paternity_or_maternity = paternity_or_maternity
        db.commit()

        return {
            "id": elf.id,
            "name": elf.name,
            "paternity_or_maternity": elf.paternity_or_maternity,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.delete("/delete_elf/{elf_id}/")
async def delete_elf(elf_id: int, db: Session = Depends(get_db)):
    try:
        elf = db.query(Elf).filter(Elf.id == elf_id).first()
        if not elf:
            raise HTTPException(status_code=404, detail="Elf not found")

        db.delete(elf)
        db.commit()

        return {"message": "Elf deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.delete("/delete_package/{item_id}/")
async def delete_item(id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(Package).filter(Package.id == id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        db.delete(item)
        db.commit()

        return {"message": "Package deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()